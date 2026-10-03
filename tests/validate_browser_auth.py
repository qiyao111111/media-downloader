"""Explicit native browser probe; emits booleans/errors, never Cookie values.

python tests/validate_browser_auth.py OUTPUT_DIRECTORY
Reads the current user's browser profiles only when explicitly run.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yt_dlp
from yt_dlp.extractor.youtube import YoutubeIE
from configs.ydl_opts import build_opts
from core.credentials import SafeLogger, redact


def validate(out):
    out.mkdir(parents=True, exist_ok=True)
    cases = [('chrome', 'Default'), ('chrome', 'Profile 1'), ('edge', 'Default')]
    firefox_root = Path(os.environ['APPDATA'])/'Mozilla/Firefox/Profiles'
    cases.extend(('firefox', str(p)) for p in firefox_root.glob('*') if (p/'cookies.sqlite').is_file())
    results = []
    for browser, profile in [(None, None), *cases]:
        result = {'browser': browser or 'anonymous', 'profile': Path(profile).name if profile else None}
        options = build_opts({'cookiesfrombrowser': (browser, profile, None, None) if browser else None,
                              'format': 'ba', 'socket_timeout': 15, 'retries': 1,
                              'quiet': True, 'logger': SafeLogger()})
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                jar = ydl.cookiejar
                result['cookie_count'] = len(jar)
                ie = YoutubeIE(ydl)
                result['native_auth_cookie_detected'] = bool(ie.is_authenticated)
                # Server-rendered public watch page distinguishes signed-in from anonymous.
                with ydl.urlopen('https://www.youtube.com/watch?v=aqz-KE-bpKQ') as response:
                    page = response.read().decode('utf-8', errors='replace')
                cfg = ie.extract_ytcfg('aqz-KE-bpKQ', page)
                result['server_logged_in'] = cfg.get('LOGGED_IN')
                result['probe'] = 'PASS'
        except Exception as exc:
            result.update(probe='FAIL', error=redact(exc))
        results.append(result)
        print(json.dumps(result), flush=True)
        (out/'browser-probes.json').write_text(json.dumps(results, indent=2), encoding='utf-8')


if __name__ == '__main__':
    validate(Path(sys.argv[1]).resolve())
