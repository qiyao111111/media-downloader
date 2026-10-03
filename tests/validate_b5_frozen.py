"""B5 local frozen Qt regression. This developer-host check is not clean Windows."""
import json,os,subprocess,sys
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from loopback import MediaServer,Proxy,USER,PASSWORD


def run(exe,out,mode):
    root=Path(__file__).resolve().parents[1];out.mkdir(parents=True,exist_ok=True)
    url='https://www.youtube.com/watch?v=E86EwGT_c2M'
    cases=[{'name':mode+'-1080','url':url,'target':1080},
           {'name':mode+'-4k','url':url,'target':2160,'metadata_only':True},
           {'name':mode+'-8k','url':url,'metadata_only':True},
           {'name':mode+'-8k60-hdr','url':'https://www.youtube.com/watch?v=hVvEISFw9w0','metadata_only':True},
           {'name':mode+'-audio','url':url,'target':'audio','audio_format':'mp3'}]
    fixture=out/'fixture.mp4'
    subprocess.run([str(root/'bin/ffmpeg.exe'),'-v','error','-y','-f','lavfi','-i','testsrc2=size=1280x720:rate=25',
                    '-f','lavfi','-i','sine=frequency=440','-t','3','-c:v','mpeg4','-c:a','aac',str(fixture)],check=True)
    server=MediaServer(fixture,require_cookie=True);proxies={s:Proxy(socks=s!='http') for s in ('http','socks5','socks5h')}
    cookies=out/'controlled-cookies.txt'
    cookies.write_text('# Netscape HTTP Cookie File\n127.0.0.1\tFALSE\t/\tFALSE\t2147483647\taudit_session\tcontrolled-test\n')
    if mode=='portable':
        cases.append({'name':mode+'-cookie','url':f'http://127.0.0.1:{server.server_address[1]}/fixture.mp4',
                      'options':{'format':'b','cookiefile':str(cookies),'http_headers':{'User-Agent':'B01-test-agent'}}})
        for scheme,proxy in proxies.items():
            endpoint=f'{scheme}://{quote(USER.decode())}:{quote(PASSWORD.decode())}@127.0.0.1:{proxy.server_address[1]}'
            cases.append({'name':mode+'-'+scheme,'url':url,'target':'audio','options':{'proxy':endpoint}})
        cases.append({'name':mode+'-cancel-retry','url':url,'target':1080,'cancel':True,'retry':True})
    spec={'evidence':str(out),'download_directory':str(out/'下载输出 Chinese spaces'),'cases':cases,
          'navigate':False,'product_checks':True,'timeout_ms':1500000}
    file=out/'acceptance.json';file.write_text(json.dumps(spec),encoding='utf-8')
    env=dict(os.environ);windows=os.environ['SystemRoot'];env['PATH']=windows+'\\System32;'+windows
    env['LOCALAPPDATA']=str(out/'isolated-user-data')
    for key in ('PYTHONPATH','QT_PLUGIN_PATH','QML2_IMPORT_PATH'):env.pop(key,None)
    try:
        code=subprocess.run([str(exe),'--validate-release',str(file)],env=env,timeout=1600).returncode
        rows=json.loads((out/'results.json').read_text(encoding='utf-8'))
        by_name={r['name']:r for r in rows}
        assert code==0 and len(rows)==len(cases)
        for suffix,height in (('1080',1080),('4k',2160),('8k',4320),('8k60-hdr',4320)):
            assert by_name[mode+'-'+suffix]['height']==height
        hdr=by_name[mode+'-8k60-hdr'];assert hdr['fps']==60 and hdr['dynamic_range'] in ('HDR10','HDR10+','HLG','HDR')
        for row in rows:
            assert all(r['selection_unchanged'] and r['download_visible'] for r in row['product_ui'])
        # Decode the complete real 1080P output through the bundled FFmpeg.
        video=by_name[mode+'-1080']['outputs'][0]
        decoded=subprocess.run([str(exe.parent/'bin/ffmpeg.exe'),'-v','error','-i',video,'-f','null','NUL'],capture_output=True,text=True)
        assert decoded.returncode==0 and not decoded.stderr
        metrics={'scope':'LOCAL DEVELOPER HOST; independent clean Windows NOT TESTED','exitcode':code,'cases':len(rows),
                 'full_1080_decode':True,'cookie_authenticated':bool(server.requests_seen) and all(r['cookie_ok'] for r in server.requests_seen),
                 'proxy_auth':{s:bool(p.records) and all(r['username_ok'] and r['password_ok'] for r in p.records) for s,p in proxies.items()}}
        if mode=='portable':
            assert metrics['cookie_authenticated'] and all(metrics['proxy_auth'].values())
            retried=by_name[mode+'-cancel-retry']
            # The retry is a new task; its state list replaces the old task's.
            assert retried['retried'] and retried['status']=='completed' and (out/'state-cancelled.png').is_file()
            metrics['cancel_retry']=True
        # Start another actual Qt process against the same persisted profile.
        restart={**spec,'evidence':str(out/'restart'),'cases':[],'navigate':False}
        restart_file=out/'restart.json';restart_file.write_text(json.dumps(restart),encoding='utf-8')
        assert subprocess.run([str(exe),'--validate-release',str(restart_file)],env=env,timeout=120).returncode==0
        saved=json.loads((out/'restart/product-startup/startup.json').read_text(encoding='utf-8'))
        assert saved['onboarding_complete'] and saved['language']=='zh' and saved['download_folder']==spec['download_directory']
        summary=json.loads((out/'summary.json').read_text(encoding='utf-8'))
        assert saved['history_count']==summary['history'] and saved['history_count']>0
        metrics['restart_persistence']=True
        (out/'host-fixtures.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics),flush=True)
    finally:
        for p in proxies.values():p.close()
        server.close();cookies.unlink(missing_ok=True)
        file.unlink(missing_ok=True) # Test-only cookie/proxy configuration stays out of evidence.


if __name__=='__main__':run(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve(),sys.argv[3])
