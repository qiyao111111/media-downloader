"""Live controlled FFmpeg merge failure; no mock download or mock FFmpeg."""

import json
import multiprocessing
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from configs.ydl_opts import build_opts
from core.task import DownloadTask


if __name__=='__main__':
    multiprocessing.freeze_support()
    out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
    finished=[];pps=[]
    def progress(tid,data):
        if data.get('status')=='finished':finished.append(data.get('info_dict',{}).get('format_id'))
    opts=build_opts({'format':'bv[height=144]+ba','merge_output_format':'mkv','socket_timeout':15,'retries':2,
                    'paths':{'home':str(out)},'outtmpl':'controlled-failure_%(id)s.%(ext)s',
                    'postprocessor_args':{'merger+ffmpeg_o':['-b01-invalid-option']},
                    'postprocessor_hooks':[lambda data:pps.append((data.get('postprocessor'),data.get('status')))]})
    task=DownloadTask('https://www.youtube.com/watch?v=aqz-KE-bpKQ',opts,on_progress=progress);task.run()
    result={'test':'real-ffmpeg-merge-failure','status':task.status.value,'downloaded_streams':finished,
            'merger_started':('Merger','started') in pps,'final_outputs':task.output_files,
            'worker_children':len(multiprocessing.active_children()),'error':str(task.error)}
    print(json.dumps(result),flush=True)
    (out/'failure-result.json').write_text(json.dumps(result),encoding='utf-8')
    assert len(finished)==2 and result['merger_started'] and task.status.value=='failed' and not task.output_files
