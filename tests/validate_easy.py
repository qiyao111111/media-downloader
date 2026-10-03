"""Windows integration check: expands the one-click EXE in the current user profile."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[1]
asset = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root/'dist/release/MediaDownloader-Easy-Windows-x64.exe'
local = Path(os.environ['LOCALAPPDATA'])
exe = local/'MediaDownloader-Easy/MediaDownloader.exe'
settings = local/'MediaDownloader/config/app_settings.json'
before = settings.read_bytes() if settings.exists() else None
windows = Path(os.environ['SystemRoot'])
env = dict(os.environ, QT_QPA_PLATFORM='offscreen', PATH=str(windows/'System32')+';'+str(windows))
for key in ('PYTHONPATH', 'QT_PLUGIN_PATH', 'QML2_IMPORT_PATH'):
    env.pop(key, None)
powershell = windows/'System32/WindowsPowerShell/v1.0/powershell.exe'
query = "Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq (Join-Path $env:LOCALAPPDATA 'MediaDownloader-Easy\\MediaDownloader.exe') } | Select-Object -ExpandProperty ProcessId"
def running():
    return {int(value) for value in subprocess.check_output([str(powershell), '-NoProfile', '-Command', query], text=True).split() if value.isdigit()}
previous = running()
launcher = subprocess.Popen([str(asset)], env=env)
created = set()
try:
    for attempt in range(60):
        created = running()-previous
        if created:
            break
        time.sleep(1)
    assert created, 'One-click package did not launch the application'
    if before is not None:
        assert settings.read_bytes() == before, 'Existing settings changed'
    else:
        defaults = json.loads(settings.read_text(encoding='utf-8'))
        assert defaults['language'] == 'zh' and defaults['onboarding_complete']
    output = root/'temp/easy-health.json'
    output.parent.mkdir(exist_ok=True)
    subprocess.run([str(exe), '--diagnostics', str(output)], env=env, check=True, timeout=30)
    health = json.loads(output.read_text(encoding='utf-8'))
    for name in ('ffmpeg', 'ffprobe', 'quickjs'):
        assert health[name]['status'] == 'READY', f'{name} is not bundled and ready'
    print(json.dumps({'auto_launch': 'PASS', 'system_only_path': 'PASS', 'runtimes': 'PASS',
                      'sha256': hashlib.sha256(asset.read_bytes()).hexdigest()}))
finally:
    for pid in created:
        subprocess.run([str(windows/'System32/taskkill.exe'), '/PID', str(pid), '/F'], stdout=subprocess.DEVNULL)
