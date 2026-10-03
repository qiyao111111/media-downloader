"""Host fixture driver. Target EXE runs with Windows-only PATH, no host Python tools."""
import json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from loopback import MediaServer,Proxy,USER,PASSWORD
from urllib.parse import quote


def run(exe,out,mode):
    out.mkdir(parents=True,exist_ok=True);root=Path(__file__).resolve().parents[1];fixture=out/'fixture.mp4'
    subprocess.run([str(root/'bin/ffmpeg.exe'),'-v','error','-y','-f','lavfi','-i','testsrc2=size=1280x720:rate=25','-f','lavfi','-i','sine=frequency=440',
                    '-t','12','-c:v','mpeg4','-q:v','2','-c:a','aac',str(fixture)],check=True)
    server=MediaServer(fixture,require_cookie=True);proxies={s:Proxy(socks=s!='http') for s in ('http','socks5','socks5h')}
    cookies=out/'controlled-cookies.txt';cookies.write_text('# Netscape HTTP Cookie File\n127.0.0.1\tFALSE\t/\tFALSE\t2147483647\taudit_session\tcontrolled-test\n')
    url='https://www.youtube.com/watch?v=E86EwGT_c2M'
    local=f'http://127.0.0.1:{server.server_address[1]}/fixture.mp4'
    cases=[{'name':mode+'-1080','url':url,'target':1080},
           {'name':mode+'-4k','url':url,'target':2160,**({'cancel':True,'retry':True} if mode=='portable' else {'metadata_only':True})},
           {'name':mode+'-8k','url':url,**({} if mode=='portable' else {'metadata_only':True})},
           {'name':mode+'-8k60-hdr','url':'https://www.youtube.com/watch?v=hVvEISFw9w0','metadata_only':True},
           {'name':mode+'-audio','url':url,'target':'audio','audio_format':'mp3'},
           {'name':mode+'-cookie','url':local,'options':{'format':'b','cookiefile':str(cookies),'http_headers':{'User-Agent':'B01-test-agent'}}}]
    for scheme,p in proxies.items():
        endpoint=f'{scheme}://{quote(USER.decode())}:{quote(PASSWORD.decode())}@127.0.0.1:{p.server_address[1]}'
        cases.append({'name':mode+'-'+scheme,'url':url,'target':'audio','options':{'proxy':endpoint}})
    # A video stream downloads long enough to exercise cancellation and active exit.
    cases += [{'name':mode+'-cancel','url':url,'target':1080,'cancel':True},
              {'name':mode+'-exit','url':url,'target':1080,'exit_active':True}]
    manifest={'evidence':str(out),'download_directory':str(out/'下载输出 中文 spaces'),'cases':cases,'navigate':True}
    file=out/'acceptance.json';file.write_text(json.dumps(manifest,indent=2))
    env=dict(os.environ);windows=os.environ['SystemRoot'];env['PATH']=windows+'\\System32;'+windows
    for key in ('PYTHONPATH','QT_PLUGIN_PATH','QML2_IMPORT_PATH'):env.pop(key,None)
    try:
        code=subprocess.run([str(exe),'--validate-release',str(file)],env=env,timeout=1800).returncode
        metrics={'exitcode':code,'isolated_PATH':env['PATH'],'cookie_authenticated':bool(server.requests_seen) and all(r['cookie_ok'] for r in server.requests_seen),
                 'proxy_requests':{s:len(p.records) for s,p in proxies.items()},'proxy_auth':{s:bool(p.records) and all(r['username_ok'] and r['password_ok'] for r in p.records) for s,p in proxies.items()}}
        (out/'host-fixtures.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics),flush=True)
        assert code==0 and metrics['cookie_authenticated'] and all(metrics['proxy_auth'].values())
    finally:
        for p in proxies.values():p.close()
        server.close()

if __name__=='__main__':run(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),sys.argv[3])
