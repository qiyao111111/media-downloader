"""Local frozen RC2 validation; never claims independent clean Windows."""
import sys,json,os,subprocess,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]

def run(mode):
    bundle=root/'dist'/('MediaDownloader-Portable' if mode=='portable' else 'MediaDownloader')
    out=root/'build/b51-rc2'/mode;out.mkdir(parents=True,exist_ok=True)
    exe=bundle/'MediaDownloader.exe';env=dict(os.environ);env['PATH']=os.environ['SystemRoot']+'\\System32;'+os.environ['SystemRoot'];env['LOCALAPPDATA']=str(root/'temp/b51-rc2-installed-profile')
    for key in ('PYTHONPATH','QT_PLUGIN_PATH','QML2_IMPORT_PATH'):env.pop(key,None)
    profile=bundle/'config' if mode=='portable' else Path(env['LOCALAPPDATA'])/'MediaDownloader/config';profile.mkdir(parents=True,exist_ok=True)
    (profile/'app_settings.json').write_text(json.dumps({'language':'en','theme':'dark','onboarding_complete':True,'window_width':1366,'window_height':768,'ffmpeg_location':str(bundle/'bin')}),encoding='utf-8')
    url='https://www.youtube.com/watch?v=E86EwGT_c2M'
    cases=[{'name':mode+'-1080','url':url,'target':1080},{'name':mode+'-4k','url':url,'target':2160,'metadata_only':True},
           {'name':mode+'-8k','url':url,'metadata_only':True},{'name':mode+'-8k60-hdr','url':'https://www.youtube.com/watch?v=hVvEISFw9w0','metadata_only':True},
           {'name':mode+'-audio','url':url,'target':'audio','audio_format':'mp3'}]
    spec={'evidence':str(out),'download_directory':str(root/'temp/b51 RC2 downloads'/mode),'cases':cases,'product_checks':True,'timeout_ms':600000}
    file=out/'acceptance.json';file.write_text(json.dumps(spec),encoding='utf-8')
    result=subprocess.run([str(exe),'--validate-release',str(file)],env=env,timeout=700);assert result.returncode==0,result.returncode
    rows=json.loads((out/'results.json').read_text(encoding='utf-8'));assert len(rows)==5
    by={r['name']:r for r in rows}
    for name,height in [('1080',1080),('4k',2160),('8k',4320),('8k60-hdr',4320)]:assert by[mode+'-'+name]['height']==height
    hdr=by[mode+'-8k60-hdr'];assert hdr['fps']==60 and hdr['dynamic_range']=='HDR10'
    for row in rows:assert all(item['selection_unchanged'] and item['download_visible'] for item in row['product_ui'])
    summary=json.loads((out/'summary.json').read_text(encoding='utf-8'));assert summary['children']==0;assert summary['health']['application']['version']=='0.9.0-rc2';assert summary['health']['application']['mode']==mode
    for tool in ('yt-dlp','ffmpeg','ffprobe','quickjs'):assert summary['health'][tool]['status']=='READY'
    for tool in ('ffmpeg','ffprobe','quickjs'):assert Path(summary['health'][tool]['path']).is_relative_to(bundle)
    decodes=[]
    for name in ('1080','audio'):
        video=Path(by[mode+'-'+name]['outputs'][0]);r=subprocess.run([str(bundle/'bin/ffmpeg.exe'),'-v','error','-i',str(video),'-f','null','NUL'],capture_output=True)
        assert r.returncode==0 and not r.stderr,r.stderr
        with video.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
        decodes.append({'case':name,'file':video.name,'bytes':video.stat().st_size,'sha256':digest,'full_decode_exit':r.returncode,'stderr':r.stderr.decode('utf-8',errors='replace')})
    metrics={'scope':'Developer-host frozen Portable and installed-mode payload; Setup was built but not reinstalled. Independent clean Windows NOT TESTED.','mode':mode,'version':'0.9.0-rc2','cases':len(rows),'exitcode':result.returncode,'missing_keys':0,'children':summary['children'],'runtime_paths_within_bundle':True,'decode':decodes}
    (out/'verification.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8');print(json.dumps(metrics),flush=True)

if __name__=="__main__":run(sys.argv[1])
