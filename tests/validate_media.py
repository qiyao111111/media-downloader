"""Live 8K acceptance: python tests/validate_media.py OUTPUT_DIRECTORY.

Full native source download, interruption/resume, video/audio/active-FFmpeg
cancellation, final ffprobe and full decode. No scaling or re-encoding.
"""

import csv
import io
import json
import multiprocessing
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from configs.ydl_opts import build_opts
from core.ffmpeg_utils import get_default_format
from core.info_extractor import extract_info
from core.task import DownloadTask


def ffmpeg_pids():
    text = subprocess.check_output(['tasklist','/FI','IMAGENAME eq ffmpeg.exe','/FO','CSV','/NH']).decode(errors='replace')
    return [int(row[1]) for row in csv.reader(io.StringIO(text)) if row and row[0].lower()=='ffmpeg.exe']


def validate(out, video_id):
    out.mkdir(parents=True,exist_ok=True)
    url='https://www.youtube.com/watch?v='+video_id
    options=build_opts({'format':get_default_format(),'merge_output_format':'mkv','socket_timeout':20,
                       'retries':3,'fragment_retries':3,'paths':{'home':str(out)},
                       'outtmpl':'native8k_%(id)s.%(ext)s'})
    info=extract_info(url,options)
    keys=('format_id','width','height','fps','vcodec','acodec','dynamic_range','tbr','vbr','ext','filesize','filesize_approx')
    formats=[{k:f.get(k) for k in keys} for f in info['requested_formats']]
    assert formats[0]['width']==7680 and formats[0]['height']==4320 and formats[0]['acodec']=='none'
    assert formats[1]['vcodec']=='none' and formats[1]['acodec']!='none'
    results=[{'test':'selected','formats':formats,'duration':info.get('duration')}]
    print(json.dumps(results[-1]),flush=True)

    def run(name,cancel=None,pp_cancel=False):
        first=[];last=[0];cancel_data=[];pids=[];baseline=ffmpeg_pids()
        def progress(tid,d):
            if not first and d.get('status') in ('downloading', 'finished'):
                first.append(d.get('downloaded_bytes',0))
            if time.monotonic()-last[0]>20:
                last[0]=time.monotonic();print(name,d.get('info_dict',{}).get('format_id'),d.get('downloaded_bytes'),flush=True)
            if cancel and cancel(d):
                cancel_data.append({k:d.get(k) for k in ('downloaded_bytes','total_bytes')});task.cancel()
        def pp(d):
            if pp_cancel and d.get('postprocessor')=='Merger' and d.get('status')=='started':
                time.sleep(.5);pids.extend(p for p in ffmpeg_pids() if p not in baseline);task.cancel()
        opts={**options,'postprocessor_hooks':[pp]}
        if name=='cancel-audio':opts['ratelimit']=2*1024*1024
        if pp_cancel:opts['postprocessor_args']={'merger+ffmpeg_i':['-readrate','1']}
        task=DownloadTask(url,opts,on_progress=progress);task.run()
        size={p.name:p.stat().st_size for p in out.glob('*.part')}
        time.sleep(.5)
        result={'test':name,'status':task.status.value,'error':str(task.error) if task.error else None,
                'first_bytes':first[0] if first else None,'cancel_progress':cancel_data,
                'part_stable':size=={p.name:p.stat().st_size for p in out.glob('*.part')},
                'ffmpeg_observed':pids,'ffmpeg_removed':not any(p in ffmpeg_pids() for p in pids),
                'active_children':len(multiprocessing.active_children()),'output_files':task.output_files}
        print(json.dumps(result),flush=True);results.append(result)
        if cancel or pp_cancel:
            assert task.status.value=='cancelled' and result['part_stable']
        if pp_cancel:assert pids and result['ffmpeg_removed']
        (out/'media-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
        return task

    run('cancel-video',lambda d:d.get('info_dict',{}).get('acodec')=='none' and
        d.get('downloaded_bytes',0)>.1*(d.get('total_bytes') or 10**15))
    run('cancel-audio',lambda d:d.get('info_dict',{}).get('vcodec')=='none' and d.get('downloaded_bytes',0)>32768)
    run('cancel-active-merge',pp_cancel=True)
    # Explicit lossless remux avoids this FFmpeg build's MKV/Opus probe warning.
    options = build_opts({**options, 'remux_video': 'mp4'})
    task=run('full');assert task.status.value=='completed' and task.output_files
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',task.output_files[0]]).decode('utf-8'))
    (out/'ffprobe.json').write_text(json.dumps(probe,indent=2),encoding='utf-8')
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert video['width']==7680 and video['height']==4320
    assert any(s['codec_type']=='audio' for s in probe['streams'])
    print('FULL_DECODE_START',flush=True)
    with (out/'decode-progress.log').open('wb') as progress, (out/'decode-errors.log').open('wb') as errors:
        code=subprocess.run(['ffmpeg','-v','error','-stats_period','10','-progress','pipe:1','-i',task.output_files[0],
                             '-fps_mode','passthrough','-enc_time_base:v','demux','-f','null','-'],
                            stdout=progress,stderr=errors).returncode
    result={'test':'full-decode','returncode':code,'error_bytes':(out/'decode-errors.log').stat().st_size,
            'duration':probe['format']['duration'],'bytes':Path(task.output_files[0]).stat().st_size}
    print(json.dumps(result),flush=True);results.append(result)
    (out/'media-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    assert code==0 and result['error_bytes']==0


if __name__=='__main__':
    multiprocessing.freeze_support()
    validate(Path(sys.argv[1]).resolve(),sys.argv[2] if len(sys.argv)>2 else 'E86EwGT_c2M')
