"""Explicit B2 live validation. Downloads whole source streams; no section limits."""
import json
import multiprocessing
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.option_builder import build_opts
from core.format_selector import normalize_formats,select_quality,build_quality_options
from core.info_extractor import extract_info
from core.task import DownloadTask
from core.ffmpeg_utils import validate_media

KEYS=('format_id','width','height','fps','dynamic_range','vcodec','acodec','ext','abr','asr','audio_channels')
def safe(f): return {k:f.get(k) for k in KEYS}

def validate(out):
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    for vid,target,download in [('E86EwGT_c2M',1080,False),('E86EwGT_c2M',2160,False),
                                ('E86EwGT_c2M','best',True),('hVvEISFw9w0','best',False)]:
        url='https://www.youtube.com/watch?v='+vid
        opts=build_opts({'quality_target':target,'socket_timeout':20,'retries':3,
                         'paths':{'home':str(out)},'outtmpl':f'{target}_%(id)s.%(ext)s'})
        info=extract_info(url,opts)
        profiles=normalize_formats(info['formats'],info.get('duration'));selection=select_quality(profiles,target)
        selected=info.get('requested_formats') or [info]
        row={'url':url,'target':target,'formats_count':len(profiles),
             'highest_height':max(p.height or 0 for p in profiles),'quality_options':len(build_quality_options(profiles)),
             'selected':[safe(f) for f in selected], 'expression':selection.yt_dlp_format_expression,
             'container':selection.final_container,'duration':info.get('duration'),'reason':selection.reason}
        assert selected[0]['height']==(target if isinstance(target,int) else 4320)
        assert info['format_id']==selection.yt_dlp_format_expression
        row['metadata_result']='PASS';results.append(row)
        (out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
        print(json.dumps(row),flush=True)
        if not download: continue
        last=[0]
        def progress(tid,data):
            if time.monotonic()-last[0]>20:
                last[0]=time.monotonic();print('bytes',data.get('downloaded_bytes'),flush=True)
        task=DownloadTask(url,opts,on_progress=progress);task.run()
        row['status']=task.status.value;row['error']=str(task.error) if task.error else None
        row['outputs']=task.output_files
        (out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
        assert task.status.value=='completed',row['error']
        probe=validate_media(task.output_files[0]);(out/'ffprobe.json').write_text(json.dumps(probe,indent=2))
        video=next(s for s in probe['streams'] if s['codec_type']=='video')
        assert (video['width'],video['height'])==(7680,4320)
        assert any(s['codec_type']=='audio' for s in probe['streams'])
        assert abs(float(probe['format']['duration'])-info['duration'])<2
        with (out/'decode-errors.log').open('wb') as err,(out/'decode-progress.log').open('wb') as log:
            code=subprocess.run(['ffmpeg','-v','error','-stats_period','10','-progress','pipe:1',
                                 '-i',task.output_files[0],'-fps_mode','passthrough','-enc_time_base:v','demux',
                                 '-f','null','-'],stdout=log,stderr=err).returncode
        row['decode_returncode']=code;row['decode_error_bytes']=(out/'decode-errors.log').stat().st_size
        row['full_download']='PASS' if code==0 and row['decode_error_bytes']==0 else 'FAIL'
        (out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
        print(json.dumps(row),flush=True)
        assert row['full_download']=='PASS'

if __name__=='__main__':
    multiprocessing.freeze_support();validate(Path(sys.argv[1]).resolve())
