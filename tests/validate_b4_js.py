"""Same formerly challenged YouTube source, without/with native Deno/EJS."""
import json,multiprocessing,sys,threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.option_builder import build_opts
from core.runtime import run_ydl
from core.manager import DownloadManager
from core.credentials import redact


def run(out):
    out.mkdir(parents=True,exist_ok=True);rows=[];manager=DownloadManager()
    for enabled in [False,True]:
        inputs={'proxy':'','download_path':str(out),'outtmpl':('with' if enabled else 'without')+'_%(id)s.%(ext)s','embed_metadata':False,'embed_chapters':False,'socket_timeout':30}
        if not enabled:inputs['js_runtimes']={}
        opts=build_opts(inputs);row={'enabled':enabled,'url':'https://www.youtube.com/watch?v=E86EwGT_c2M','preview':'FAIL','download':'NOT TESTED','error':''}
        try:
            info=run_ydl(row['url'],opts,threading.Event(),preview=True);profiles=manager.preview_formats(info)
            row.update(preview='PASS',formats=len(info.get('formats') or []),highest=max((p.height or 0 for p in profiles),default=0))
            opts,selection=manager.prepare_download(inputs,info,1080)
            outputs=run_ydl(row['url'],opts,threading.Event());row.update(download='PASS',outputs=outputs,selection=selection.yt_dlp_format_expression)
        except Exception as error:row['error']=redact(error)
        rows.append(row);out.joinpath('comparison.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
    manager.shutdown()

if __name__=='__main__':multiprocessing.freeze_support();run(Path(sys.argv[1]).resolve())
