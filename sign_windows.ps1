# Sign the application, rebuild the one-click package, then sign the package.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidatePattern('^[A-Fa-f0-9]{40}$')][string]$Thumbprint,
    [Parameter(Mandatory = $true)][string]$SignTool,
    [Parameter(Mandatory = $true)][string]$InnoCompiler,
    [string]$Python = "$PSScriptRoot\.venv\Scripts\python.exe",
    [string]$TimestampServer = 'https://timestamp.digicert.com',
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$cert = Get-Item -LiteralPath "Cert:\CurrentUser\My\$Thumbprint"
if (-not $cert.HasPrivateKey -or $cert.NotAfter -le (Get-Date) -or $cert.NotBefore -gt (Get-Date)) {
    throw 'A current code-signing certificate with an accessible private key is required.'
}
if (-not ($cert.EnhancedKeyUsageList.ObjectId -contains '1.3.6.1.5.5.7.3.3')) {
    throw 'The certificate does not permit code signing.'
}
$chain = New-Object System.Security.Cryptography.X509Certificates.X509Chain
try {
    if ($cert.Subject -eq $cert.Issuer -or -not $chain.Build($cert)) {
        throw 'The certificate must chain to a trusted issuer; self-signed certificates are unsuitable.'
    }
} finally { $chain.Dispose() }
foreach ($tool in @($SignTool, $InnoCompiler, $Python)) {
    if (-not (Test-Path -LiteralPath $tool -PathType Leaf)) { throw "Missing tool: $tool" }
}
$payload = Join-Path $PSScriptRoot 'dist\MediaDownloader\MediaDownloader.exe'
if (-not (Test-Path -LiteralPath $payload)) { throw 'Build the complete Windows payload first.' }
if ($CheckOnly) { Write-Output 'Certificate, signing tools and payload are ready.'; return }
function Sign-AndVerify([string]$File) {
    & $SignTool sign /sha1 $Thumbprint /fd SHA256 /tr $TimestampServer /td SHA256 $File
    if ($LASTEXITCODE -ne 0) { throw "Signing failed: $File" }
    & $SignTool verify /pa /all $File
    if ($LASTEXITCODE -ne 0) { throw "Signature verification failed: $File" }
    $signature = Get-AuthenticodeSignature -LiteralPath $File
    if ($signature.Status -ne 'Valid' -or -not $signature.TimeStamperCertificate -or
        $signature.SignerCertificate.Thumbprint -ne $Thumbprint.ToUpperInvariant()) {
        throw "A valid signature from the requested publisher with a timestamp is required: $File"
    }
}
Push-Location $PSScriptRoot
try {
    $version = & $Python -c 'from app.version import VERSION; print(VERSION)'
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read application version.' }
    $windowsVersion = & $Python -c "from app.version import WINDOWS_VERSION; print('.'.join(map(str,WINDOWS_VERSION)))"
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read Windows version.' }
    Sign-AndVerify $payload
    & $Python -c "import json; from pathlib import Path; from release_licenses import inspect_bundle; p=Path('dist/MediaDownloader'); (p/'licenses/bundle-file-inventory.json').write_text(json.dumps(inspect_bundle(p),indent=2),encoding='utf-8')"
    if ($LASTEXITCODE -ne 0) { throw 'Cannot update signed payload inventory.' }
    & $InnoCompiler /Q "/DAppVersion=$version" "/DWindowsVersion=$windowsVersion" 'build\easy.iss'
    if ($LASTEXITCODE -ne 0) { throw 'One-click package rebuild failed.' }
    $release = Join-Path $PSScriptRoot 'dist\release\MediaDownloader-Easy-Windows-x64.exe'
    Sign-AndVerify $release
    $digest = (Get-FileHash -LiteralPath $release -Algorithm SHA256).Hash.ToLowerInvariant()
    "$digest  MediaDownloader-Easy-Windows-x64.exe" | Set-Content -LiteralPath 'dist\release\SHA256SUMS.txt' -Encoding ascii
    Write-Output 'Signed package is ready. Re-run validation before uploading; signing does not guarantee SmartScreen reputation.'
} finally { Pop-Location }
