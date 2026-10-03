"""Native yt-dlp/EJS A/B; no challenge-solver or selector changes."""
import json,multiprocessing,sys,threading,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.option_builder import build_opts
from core.runtime import run_ydl
from core.format_selector import normalize_formats,select_quality
from core.credentials import redact
import yt_dlp


class ChallengeLogger:
    def __init__(self):self.solvers=[];self.challenge_errors=0
    def debug(self,message):
        if 'Solving JS challenges using ' in message:
            self.solvers.append(message.split('Solving JS challenges using ',1)[1].split()[0])
    def warning(self,message):
        if 'challenge' in message.lower():self.challenge_errors+=1
    error=warning


def run(out,quickjs):
    out.mkdir(parents=True,exist_ok=True);rows=[]
    runtimes={'deno':Path('bin/runtime/deno.exe').resolve(),'quickjs':quickjs}
    for name,path in runtimes.items():
        for video in ('E86EwGT_c2M','hVvEISFw9w0'):
            start=time.monotonic();row={'runtime':name,'runtime_path':str(path),'video':video}
            try:
                opts=build_opts({'proxy':'','js_runtimes':{name:{'path':str(path)}},'socket_timeout':30,
                                 'cachedir':str(out/name/video),'embed_metadata':False,'embed_chapters':False})
                info=run_ydl('https://www.youtube.com/watch?v='+video,opts,threading.Event(),preview=True)
                profiles=normalize_formats(info['formats'],info.get('duration'));best=select_quality(profiles,'best')
                selected=best.video
                row.update(result='PASS',preview_seconds=round(time.monotonic()-start,3),formats_count=len(info['formats']),
                           highest={'format_id':selected.format_id,'width':selected.width,'height':selected.height,
                                    'fps':selected.fps,'dynamic_range':selected.dynamic_range,'vcodec':selected.video_codec},
                           selection=best.yt_dlp_format_expression,
                           video_formats=[{'id':p.format_id,'width':p.width,'height':p.height,'fps':p.fps,'range':p.dynamic_range,'codec':p.video_codec} for p in profiles if p.width and p.height])
                assert selected.height==4320
                if video=='hVvEISFw9w0':assert selected.fps==60 and selected.dynamic_range=='HDR10'
            except Exception as error:row.update(result='FAIL',error=redact(error),preview_seconds=round(time.monotonic()-start,3))
            rows.append(row);(out/'comparison.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in row.items() if k!='video_formats'}),flush=True)
    assert len(rows)==4 and all(r['result']=='PASS' for r in rows)
    for offset in (0,1):assert rows[offset]['video_formats']==rows[offset+2]['video_formats']
    challenges=[]
    for name,path in runtimes.items():
        logger=ChallengeLogger();start=time.monotonic()
        opts=build_opts({'js_runtimes':{name:{'path':str(path)}},'logger':logger,'verbose':True,
                         'quiet':True,'cachedir':False,'skip_download':True,'socket_timeout':30,
                         'extractor_args':{'youtube':{'player_client':['web_safari','mweb'],'formats':['missing_pot']}}})
        with yt_dlp.YoutubeDL(opts) as ydl:info=ydl.extract_info('https://www.youtube.com/watch?v=E86EwGT_c2M',download=False,process=False)
        row={'runtime':name,'solvers_observed':logger.solvers,'challenge_errors':logger.challenge_errors,
             'formats_count':len(info['formats']),'seconds':round(time.monotonic()-start,3)}
        challenges.append(row);print(json.dumps(row),flush=True)
        (out/'challenge-probe.json').write_text(json.dumps(challenges,indent=2),encoding='utf-8')
        assert logger.challenge_errors==0


if __name__=='__main__':multiprocessing.freeze_support();run(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
