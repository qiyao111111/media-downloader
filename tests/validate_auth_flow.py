"""Explicit real Preview/Download auth regression; no Cookie contents in output."""
import json
import multiprocessing
import os
import pickle
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from configs.ydl_opts import build_opts
from configs.presets import BUILTIN_PRESETS
from core.runtime import run_ydl
from core.task import DownloadTask
from core.credentials import redact


def validate(out, only=None):
    out.mkdir(parents=True, exist_ok=True)
    url = 'https://www.youtube.com/watch?v=E86EwGT_c2M'
    corrupt = out/'invalid-cookies.txt'
    corrupt.write_text('# Netscape HTTP Cookie File\n.invalid\tTRUE\t/\tFALSE\tinvalid\tSID\tDUMMY_SECRET_DO_NOT_LOG\n', encoding='utf-8')
    firefox = Path(os.environ['APPDATA'])/'Mozilla/Firefox/Profiles'
    cases = [('anonymous-1080p', BUILTIN_PRESETS['1080p']),
             ('chrome-default', {'cookiesfrombrowser': ('chrome', 'Default', None, None)}),
             ('chrome-profile-1', {'cookiesfrombrowser': ('chrome', 'Profile 1', None, None)}),
             ('edge-default', {'cookiesfrombrowser': ('edge', 'Default', None, None)}),
             ('missing-browser', {'cookiesfrombrowser': ('not-a-browser',)}),
             ('missing-profile', {'cookiesfrombrowser': ('edge', 'B02-nonexistent-profile', None, None)}),
             ('corrupt-cookiefile', {'cookiefile': str(corrupt)})]
    cases.extend(('firefox-'+p.name, {'cookiesfrombrowser': ('firefox', str(p), None, None)})
                 for p in firefox.glob('*') if (p/'cookies.sqlite').is_file())
    results = []
    for name, auth in cases:
        if only and name != only:
            continue
        options = build_opts({'format': 'ba', 'socket_timeout': 15, 'retries': 1,
                              'extractor_retries': 1, 'paths': {'home': str(out)},
                              'outtmpl': name+'_%(id)s.%(ext)s', **auth})
        row = {'test': name, 'browser_spec': options.get('cookiesfrombrowser'),
               'source': 'browser' if options.get('cookiesfrombrowser') else ('file' if options.get('cookiefile') else 'anonymous'),
               'proxy': options['proxy']}
        try:
            info = run_ydl(url, options, threading.Event(), preview=True)
            row['preview'] = 'PASS'
            row['selected'] = [{k: f.get(k) for k in ('format_id', 'width', 'height', 'vcodec', 'acodec')}
                               for f in info.get('requested_formats', [info])]
        except Exception as exc:
            row.update(preview='FAIL', preview_error=redact(exc))
        task = DownloadTask(url, options)
        task.run()
        row.update(download='PASS' if task.status.value == 'completed' else 'FAIL',
                   status=task.status.value, error=str(task.error) if task.error else None,
                   context_identical=pickle.dumps(options) == pickle.dumps(task.ydl_opts),
                   nonempty_outputs=bool(task.output_files) and all(Path(p).stat().st_size > 0 for p in task.output_files),
                   children=len(multiprocessing.active_children()))
        if task.output_files and name == 'anonymous-1080p':
            import subprocess
            probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', task.output_files[0]]))
            row['streams'] = [{k: s.get(k) for k in ('codec_type','width','height','codec_name')} for s in probe['streams']]
            assert any(s.get('height') == 1080 for s in probe['streams'])
            assert any(s['codec_type'] == 'audio' for s in probe['streams'])
        print(json.dumps(row), flush=True)
        results.append(row)
        (out/'auth-flow-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
        assert row['context_identical'] and row['children'] == 0
        if name in ('missing-browser','missing-profile','corrupt-cookiefile'):
            assert row['preview'] == 'FAIL' and row['status'] == 'failed'
            assert 'DUMMY_SECRET_DO_NOT_LOG' not in json.dumps(row)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    validate(Path(sys.argv[1]).resolve(), sys.argv[2] if len(sys.argv) > 2 else None)
