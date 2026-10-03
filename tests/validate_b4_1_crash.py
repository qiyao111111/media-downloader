"""Force-stop an active frozen download, restart, then cancel/retry a fixture."""
import json,os,subprocess,sys,time
from pathlib import Path
from loopback import MediaServer


def run(exe,out,baseline):
    out.mkdir(parents=True,exist_ok=True)
    original=json.loads((baseline/'summary.json').read_text());paths=original['paths']
    settings=Path(paths['config_dir'])/'app_settings.json';history=Path(paths['data_dir'])/'download_history.json'
    before=json.loads(settings.read_text(encoding='utf-8'));records=json.loads(history.read_text(encoding='utf-8'))
    assert before['retries']==7 and before['max_workers']==1
    env=dict(os.environ);windows=os.environ['SystemRoot'];env['PATH']=windows+'\\System32;'+windows
    for key in ('PYTHONPATH','QT_PLUGIN_PATH','QML2_IMPORT_PATH'):env.pop(key,None)
    server=MediaServer(baseline/'fixture.mp4',slow=True)
    manifest=out/'crash.json';folder=Path(before['download_path']);name='b41-active-crash-'+str(time.time_ns())
    case={'name':name,'url':f'http://127.0.0.1:{server.server_address[1]}/fixture.mp4','options':{'format':'b'}}
    manifest.write_text(json.dumps({'evidence':str(out/'interrupted'),'download_directory':str(folder),'cases':[case]}))
    process=subprocess.Popen([str(exe),'--validate-release',str(manifest)],env=env)
    try:
        start=time.monotonic()
        while True:
            assert process.poll() is None and time.monotonic()-start<90
            active=json.loads(history.read_text(encoding='utf-8'))
            parts=list(folder.glob(name+'*.part'))
            # History persists the queued row until terminal state; live progress is in memory.
            if parts and parts[0].stat().st_size>1024**2 and any(r['url']==case['url'] and r['status'] not in ('completed','cancelled','failed') for r in active):break
            time.sleep(.05)
        interrupted={'pid':process.pid,'part_bytes':parts[0].stat().st_size,'active_history':True}
    finally:
        if process.poll() is None:subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],check=True,capture_output=True)
        process.wait(timeout=15)
        server.close()
    manifest.write_text(json.dumps({'evidence':str(out/'restart'),'download_directory':str(folder),'cases':[]}))
    subprocess.run([str(exe),'--validate-release',str(manifest)],env=env,check=True,timeout=60)
    after=json.loads(settings.read_text(encoding='utf-8'));restored=json.loads(history.read_text(encoding='utf-8'))
    assert all(after[k]==before[k] for k in ('download_path','retries','max_workers'))
    assert len(restored)==len(records)+1 and all(r['status'] in ('completed','cancelled','failed') for r in restored)
    recovered=next(r for r in restored if r['url']==case['url']);assert recovered['status']=='cancelled'
    health=json.loads((out/'restart/summary.json').read_text())['health']
    assert all(health[k]['status']=='READY' for k in ('yt-dlp','ffmpeg','ffprobe','quickjs' if 'quickjs' in health else 'deno'))
    server=MediaServer(baseline/'fixture.mp4',slow=True)
    try:
        case={'name':'b41-fixture-retry-'+str(time.time_ns()),'url':f'http://127.0.0.1:{server.server_address[1]}/fixture.mp4','cancel':True,'retry':True,'options':{'format':'b'}}
        manifest.write_text(json.dumps({'evidence':str(out/'retry'),'download_directory':str(folder),'cases':[case]}))
        subprocess.run([str(exe),'--validate-release',str(manifest)],env=env,check=True,timeout=120)
        retry=json.loads((out/'retry/results.json').read_text(encoding='utf-8'))[0]
        assert retry['status']=='completed' and retry['retried'] and retry['resume_first_bytes']>1024**2
    finally:server.close()
    result={'scope':'local frozen '+paths['mode']+'; clean Windows NOT TESTED','forced_active_process_tree':interrupted,
            'settings_readable_and_preserved':True,'history_readable_and_recovered':True,'runtime_health':True,'cancel_retry':True,
            'original_history_records':len(records),'recovered_history_records':len(restored),'termination_method':'taskkill /PID observed_main_pid /T /F'}
    (out/'crash-recovery.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))


if __name__=='__main__':run(*(Path(p).resolve() for p in sys.argv[1:4]))
