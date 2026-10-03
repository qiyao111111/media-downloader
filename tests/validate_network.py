"""Explicit live test: python tests/validate_network.py OUTPUT_DIRECTORY.

Uses loopback authenticated forwarders, public YouTube audio and a Cookie-gated
local fixture. It never reads personal browser cookies or exports authentication.
"""

import json
import multiprocessing
import subprocess
import sys
import threading
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from configs.ydl_opts import build_opts
from core.info_extractor import extract_info
from core.task import DownloadTask
from loopback import MediaServer, Proxy, USER, PASSWORD


def validate(out, fixture_ffmpeg='ffmpeg', fixture_codec='libx264'):
    out.mkdir(parents=True, exist_ok=True)
    results = []
    url = 'https://www.youtube.com/watch?v=aqz-KE-bpKQ'
    shared = {'format': 'ba', 'socket_timeout': 15, 'retries': 1, 'extractor_retries': 1,
              'paths': {'home': str(out)}}
    direct_options = build_opts(shared)
    info = extract_info(url, direct_options)
    results.append({'test':'no-proxy-preview','title_present':bool(info.get('title')),'format':'ba','proxy':direct_options['proxy']})
    for scheme in ('http', 'socks5', 'socks5h'):
        proxy = Proxy(socks=scheme != 'http')
        try:
            endpoint = f'{scheme}://{quote(USER.decode())}:{quote(PASSWORD.decode())}@127.0.0.1:{proxy.server_address[1]}'
            options = build_opts({**shared, 'proxy':endpoint, 'outtmpl':scheme+'_%(id)s.%(ext)s'})
            info = extract_info(url, options)
            preview_count = len(proxy.records)
            task = DownloadTask(url, options); task.run()
            failed_attempts=[]
            if task.status.value=='failed' and '403' in str(task.error):
                failed_attempts.append('HTTP 403; fresh extraction/retry')
                extract_info(url,options)
                task=DownloadTask(url,options);task.run()
            download_records = proxy.records[preview_count:]
            result = {'test':scheme,'proxy_host':'127.0.0.1','proxy_port':proxy.server_address[1],
                      'preview_requests':preview_count,'download_requests':len(download_records),
                      'same_option_snapshot':task.ydl_opts['proxy']==options['proxy'],
                      'all_auth_valid':bool(proxy.records) and all(r['username_ok'] and r['password_ok'] for r in proxy.records),
                      'address_types':sorted({r.get('address_type') for r in proxy.records if 'address_type' in r}),
                      'cdn_download':any('googlevideo.com' in r['host'] for r in download_records) if scheme in ('http','socks5h') else bool(download_records),
                      'status':task.status.value,'failed_attempts':failed_attempts,'outputs_nonempty':bool(task.output_files) and all(Path(p).stat().st_size>0 for p in task.output_files),
                      'active_children':len(multiprocessing.active_children())}
            print(json.dumps(result),flush=True); results.append(result)
            assert preview_count and download_records and task.status.value=='completed' and result['all_auth_valid']
        finally:
            proxy.close()
    fixture = out/'fixture.mp4'
    subprocess.run([fixture_ffmpeg,'-v','error','-y','-f','lavfi','-i','testsrc2=size=320x180:rate=25',
                    '-f','lavfi','-i','sine=frequency=440:sample_rate=44100','-t','3','-c:v',fixture_codec,
                    '-c:a','aac',str(fixture)],check=True)
    server = MediaServer(fixture,require_cookie=True)
    try:
        cookiefile = out/'controlled-cookies.txt'
        cookiefile.write_text('# Netscape HTTP Cookie File\n127.0.0.1\tFALSE\t/\tFALSE\t2147483647\taudit_session\tcontrolled-test\n',encoding='utf-8')
        local=f'http://127.0.0.1:{server.server_address[1]}/fixture.mp4'
        options=build_opts({'format':'b','proxy':'','cookiefile':str(cookiefile),'http_headers':{'User-Agent':'B01-test-agent'},
                            'paths':{'home':str(out)},'outtmpl':'cookie-result.%(ext)s','retries':0,'socket_timeout':5})
        info=extract_info(local,options);preview_requests=list(server.requests_seen);server.requests_seen.clear()
        task=DownloadTask(local,options);task.run()
        result={'test':'cookiefile','preview_authenticated':bool(preview_requests) and all(r['cookie_ok'] for r in preview_requests),
                'download_authenticated':bool(server.requests_seen) and all(r['cookie_ok'] for r in server.requests_seen),
                'user_agent_consistent':all(r['ua_ok'] for r in preview_requests+server.requests_seen),'status':task.status.value,
                'active_children':len(multiprocessing.active_children())}
        print(json.dumps(result),flush=True);results.append(result)
        assert result['preview_authenticated'] and result['download_authenticated'] and task.status.value=='completed'
        failed=DownloadTask(local.replace('/fixture','/fail'),options);failed.run()
        results.append({'test':'download-failure','status':failed.status.value,'active_children':len(multiprocessing.active_children())})
        assert failed.status.value=='failed'
    finally:
        server.close()
    # Separate video/audio requires FFmpeg; a deliberately missing location must fail.
    options=build_opts({**shared,'format':'bv+ba','ffmpeg_location':str(out/'missing-ffmpeg'), 'outtmpl':'merge-fail.%(ext)s'})
    task=DownloadTask(url,options);task.run()
    results.append({'test':'missing-ffmpeg','status':task.status.value,'output_count':len(task.output_files),
                    'active_children':len(multiprocessing.active_children())})
    assert task.status.value=='failed'
    (out/'network-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')


if __name__=='__main__':
    multiprocessing.freeze_support()
    validate(Path(sys.argv[1]).resolve())
