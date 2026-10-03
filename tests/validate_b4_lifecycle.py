"""Local frozen restart/crash/path checks; host fixtures are not app dependencies."""
import ctypes
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from loopback import MediaServer


def run(exe, out, runtime_evidence):
    out.mkdir(parents=True, exist_ok=True)
    original=json.loads((runtime_evidence/'summary.json').read_text())
    paths=original['paths'];settings=Path(paths['config_dir'])/'app_settings.json'
    history=Path(paths['data_dir'])/'download_history.json'
    before=json.loads(settings.read_text(encoding='utf-8'))
    records=json.loads(history.read_text(encoding='utf-8'))
    env=dict(os.environ);windows=os.environ['SystemRoot'];env['PATH']=windows+'\\System32;'+windows
    for key in ('PYTHONPATH','QT_PLUGIN_PATH','QML2_IMPORT_PATH'):env.pop(key,None)
    results={'mode':paths['mode'],'history_before':len(records),'settings_saved':before['retries']==7 and before['max_workers']==1}
    assert results['settings_saved']
    # Observe only this process's visible top-level window, then simulate a crash.
    user32=ctypes.windll.user32
    callback_type=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
    def window_ready(pid):
        found=[]
        @callback_type
        def inspect(hwnd,_):
            owner=ctypes.c_ulong();user32.GetWindowThreadProcessId(ctypes.c_void_p(hwnd),ctypes.byref(owner))
            if owner.value==pid and user32.IsWindowVisible(ctypes.c_void_p(hwnd)):found.append(hwnd)
            return True
        user32.EnumWindows(inspect,0)
        return bool(found)
    for label in ('first_observed_start','warm_start'):
        start=time.monotonic();process=subprocess.Popen([str(exe)],env=env)
        try:
            while not window_ready(process.pid):
                assert process.poll() is None and time.monotonic()-start<30
                time.sleep(.02)
            results[label+'_seconds']=round(time.monotonic()-start,3)
        finally:
            process.kill();process.wait(timeout=15)
    results['forced_termination']=True
    manifest=out/'restart.json'
    manifest.write_text(json.dumps({'evidence':str(out/'restart'),'download_directory':before['download_path'],'cases':[]}))
    subprocess.run([str(exe),'--validate-release',str(manifest)],env=env,check=True,timeout=60)
    after=json.loads(settings.read_text(encoding='utf-8'));after_history=json.loads(history.read_text(encoding='utf-8'))
    results['settings_restart']=all(after[k]==before[k] for k in ('retries','max_workers','download_path'))
    results['history_restart']=len(after_history)==len(records)
    results['history_all_terminal']=all(r['status'] in ('completed','failed','cancelled') for r in after_history)
    assert results['settings_restart'] and results['history_restart'] and results['history_all_terminal']
    # Exercise a long Chinese/space destination below Windows' 260-character boundary.
    longdir=Path(r'D:\下载测试\YouTube视频\B4_3 长路径')/('segment with spaces '*6).strip()/('中文路径 '*10).strip()
    server=MediaServer(runtime_evidence/'fixture.mp4',require_cookie=False)
    try:
        case={'name':'long-path','url':f'http://127.0.0.1:{server.server_address[1]}/fixture.mp4','options':{'format':'b'}}
        manifest.write_text(json.dumps({'evidence':str(out/'long-path'),'download_directory':str(longdir),'cases':[case]}))
        subprocess.run([str(exe),'--validate-release',str(manifest)],env=env,check=True,timeout=120)
        output=longdir/'long-path_fixture.mp4'
        results['long_path']={'length':len(str(output)),'exists':output.is_file(),'size':output.stat().st_size}
    finally:server.close()
    # Restore the user's saved test destination through the real settings flow.
    manifest.write_text(json.dumps({'evidence':str(out/'restore'),'download_directory':before['download_path'],'cases':[]}))
    subprocess.run([str(exe),'--validate-release',str(manifest)],env=env,check=True,timeout=60)
    js_name='quickjs' if 'quickjs' in original['health'] else 'deno'
    js=Path(paths['runtime_dir'])/('runtime/qjs.exe' if js_name=='quickjs' else 'runtime/deno.exe');hidden=js.with_suffix('.disabled')
    js.rename(hidden)
    try:
        subprocess.run([str(exe),'--diagnostics',str(out/'without-js.json')],env=env,check=True,timeout=30)
        results['missing_js_optional']=json.loads((out/'without-js.json').read_text())[js_name]['status']=='NOT_INSTALLED'
        manifest.write_text(json.dumps({'evidence':str(out/'without-js'),'download_directory':before['download_path'],'cases':[{'name':'without-js','url':'https://www.youtube.com/watch?v=E86EwGT_c2M','metadata_only':True}]}))
        subprocess.run([str(exe),'--validate-release',str(manifest)],env=env,check=True,timeout=120)
    finally:hidden.rename(js)
    results['startup_scope']='first observed / warm on an existing Windows installation; not an OS cold-cache benchmark'
    (out/'lifecycle.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps(results),flush=True)


if __name__=='__main__':run(*(Path(arg).resolve() for arg in sys.argv[1:4]))
