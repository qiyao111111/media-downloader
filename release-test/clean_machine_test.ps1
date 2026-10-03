param(
    [string]$PortableRoot = '',
    [string]$InstallerRoot = '',
    [string]$OutputDirectory = (Join-Path $PSScriptRoot 'reports'),
    [string]$Stage = 'unspecified'
)
# Read-only system inspection. Only the report directory and optional application
# diagnostics are written. No installation, PATH/policy changes, or process control.
$ErrorActionPreference = 'Stop'
# Load this host's built-in module even when launched through a process that
# inherited another PowerShell version's PSModulePath; do not change that path.
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Utility\Microsoft.PowerShell.Utility.psd1')
$reportDirectory = Join-Path $OutputDirectory (Get-Date -Format 'yyyyMMdd-HHmmss-fff')
New-Item -ItemType Directory -Path $reportDirectory -Force | Out-Null
$os = Get-CimInstance Win32_OperatingSystem
$report = [ordered]@{
    TimestampUtc = [DateTime]::UtcNow.ToString('o')
    Stage = $Stage
    ComputerName = $env:COMPUTERNAME
    Windows = $os.Caption
    Version = $os.Version
    Architecture = $os.OSArchitecture
    PowerShellVersion = $PSVersionTable.PSVersion.ToString()
    PATH = $env:PATH
    IndependentEnvironment = 'NOT VERIFIED - tester must establish independent guest/PC'
    CleanMachine = 'NOT TESTED - functional checklist is separate'
    SystemChanges = 'NONE'
    Dependencies = [ordered]@{}
    ArtifactChecksums = @()
    RuntimeDiagnostics = @()
    ObservedProcesses = @()
}
$where = Join-Path $env:SystemRoot 'System32\where.exe'
foreach ($name in @('python','py','yt-dlp','ffmpeg','ffprobe','qjs')) {
    # Do not execute python/py: WindowsApps stubs can open the Store.
    # Windows PowerShell 5.1 represents native stderr as an ErrorRecord.
    # A missing executable is expected evidence, not a terminating script error.
    $ErrorActionPreference = 'Continue'
    try {$found = @(& $where $name 2>$null); $code = $LASTEXITCODE}
    finally {$ErrorActionPreference = 'Stop'}
    $report.Dependencies[$name] = [ordered]@{
        Command = "where.exe $name"
        ExitCode = $code
        Result = $(if ($code -eq 0) {'PATH ENTRY FOUND - not executed; may be an alias'} else {'NOT FOUND'})
        Paths = $found
    }
}
$checksumFile = Join-Path $PSScriptRoot 'checksums.txt'
if (Test-Path -LiteralPath $checksumFile) {
    foreach ($line in Get-Content -LiteralPath $checksumFile) {
        if ($line -notmatch '^([a-fA-F0-9]{64})  (MediaDownloader-Portable.zip|MediaDownloader-Setup.exe)$') {
            throw 'Invalid checksum record; expected the two kit artifact names'
        }
        $expected = $Matches[1]; $name = $Matches[2]
        $file = Join-Path $PSScriptRoot $name
        $actual = $(if (Test-Path -LiteralPath $file) {(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash} else {''})
        $report.ArtifactChecksums += [ordered]@{File=$name; Expected=$expected; Actual=$actual; Match=($actual -eq $expected)}
    }
}
foreach ($entry in @(@{Mode='portable';Root=$PortableRoot}, @{Mode='installed';Root=$InstallerRoot})) {
    if (-not $entry.Root) {continue}
    $root = [IO.Path]::GetFullPath($entry.Root).TrimEnd('\')
    $exe = Join-Path $root 'MediaDownloader.exe'
    $result = [ordered]@{Mode=$entry.Mode; Root=$root; Executable=$exe; Status='NOT TESTED'; PathsWithinRoot=[ordered]@{}}
    if (Test-Path -LiteralPath $exe) {
        $file = Join-Path $reportDirectory ($entry.Mode + '-runtime-health.json')
        # Wait for this supplied application's diagnostics; no GUI automation.
        $process = Start-Process -FilePath $exe -ArgumentList @('--diagnostics',('"' + $file + '"')) -WindowStyle Hidden -PassThru -Wait
        $result.ExitCode = $process.ExitCode
        if ($process.ExitCode -eq 0 -and (Test-Path -LiteralPath $file)) {
            $health = Get-Content -LiteralPath $file -Raw -Encoding UTF8 | ConvertFrom-Json
            $result.Health = $health
            $result.Status = 'DIAGNOSTICS COLLECTED - not functional PASS'
            $result.ModeMatches = ($health.application.mode -eq $entry.Mode)
            foreach ($tool in @('ffmpeg','ffprobe','quickjs')) {
                $path = $health.$tool.path
                $result.PathsWithinRoot[$tool] = [bool]($path -and [IO.Path]::GetFullPath($path).StartsWith($root + '\',[StringComparison]::OrdinalIgnoreCase))
            }
            $result.EmbeddedYtDlp = $exe + '!PYZ.pyz/yt_dlp (package presence must be confirmed against payload inventory)'
        } else {$result.Status = 'DIAGNOSTICS FAILED'}
    } else {$result.Status = 'EXECUTABLE NOT FOUND'}
    $report.RuntimeDiagnostics += $result
}
$filter = "Name='MediaDownloader.exe' OR Name='ffmpeg.exe' OR Name='ffprobe.exe' OR Name='qjs.exe' OR Name='deno.exe'"
foreach ($process in Get-CimInstance Win32_Process -Filter $filter) {
    # Paths only. Do not collect command lines, cookies, headers or environment secrets.
    $report.ObservedProcesses += [ordered]@{Name=$process.Name;PID=$process.ProcessId;ParentPID=$process.ParentProcessId;ExecutablePath=$process.ExecutablePath}
}
$json = Join-Path $reportDirectory 'clean-machine-report.json'
$report | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath $json -Encoding UTF8
@(
    '# Clean Windows evidence collection'
    ''
    "Computer: $($report.ComputerName)"
    "Stage: $($report.Stage)"
    "Windows: $($report.Windows) $($report.Version) / $($report.Architecture)"
    'Independent Environment: NOT VERIFIED (tester confirmation required)'
    'Clean Machine: NOT TESTED (complete the manual checklist)'
    'System modifications by script: NONE'
    ''
    "Machine-readable evidence: $json"
    'No functional PASS is inferred from dependency absence or diagnostics.'
) | Set-Content -LiteralPath (Join-Path $reportDirectory 'clean-machine-report.md') -Encoding UTF8
Write-Output $json
