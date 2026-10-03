"""Live B3 desktop acceptance: real Analyze/controls/Download/Queue/History."""
import json,multiprocessing,subprocess,sys,time
from pathlib import Path
from unittest.mock import patch
from urllib.parse import quote
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QMessageBox
from configs.app_settings import AppSettings
from services.history_service import HistoryService
from services.logging_service import configure_logging
from core.ffmpeg_utils import validate_media
from gui.main_window import MainWindow
from models.download import TaskStatus
from loopback import MediaServer,Proxy,USER,PASSWORD


def validate(out, only=None):
    out.mkdir(parents=True,exist_ok=True);save=Path(r'D:\下载测试\YouTube视频\B3验证');save.mkdir(parents=True,exist_ok=True)
    configure_logging(out/'logs/desktop.log')
    fixture=out/'fixture.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=320x180:rate=25','-f','lavfi','-i','sine=frequency=440','-t','3','-c:v','libx264','-c:a','aac',str(fixture)],check=True)
    server=MediaServer(fixture,require_cookie=True)
    cookies=out/'controlled-cookies.txt';cookies.write_text('# Netscape HTTP Cookie File\n127.0.0.1\tFALSE\t/\tFALSE\t2147483647\taudit_session\tcontrolled-test\n')
    proxies={scheme:Proxy(socks=scheme!='http') for scheme in ('http','socks5','socks5h')}
    url='https://www.youtube.com/watch?v=E86EwGT_c2M'
    cases=[('1080p',url,1080,{}),('4k-resume',url,2160,{}),('8k',url,'best',{}),
           ('8k60-hdr','https://www.youtube.com/watch?v=hVvEISFw9w0','metadata',{}),
           ('audio',url,'audio',{}),('cookiefile',f'http://127.0.0.1:{server.server_address[1]}/fixture.mp4','custom',{'format':'b','cookiefile':str(cookies)})]
    for scheme,proxy in proxies.items():
        endpoint=f'{scheme}://{quote(USER.decode())}:{quote(PASSWORD.decode())}@127.0.0.1:{proxy.server_address[1]}'
        cases.append((scheme,url,'audio',{'proxy':endpoint}))
    cases.append(('custom',url,'custom',{'format':'bv[height<=720]+ba/b'}))
    cases.append(('playlist','https://www.youtube.com/playlist?list=PLt5yu3-wZAlSLRHmI1qNm0wjyVNWw1pCU','playlist',{}))
    responsive=only=='responsiveness'
    if responsive:cases=[(f'responsive-{height}',url,height,{}) for height in (1080,2160,4320)]
    elif only: cases=[case for case in cases if case[0]==only]
    app=QApplication([]);results=[];index=[-1];current=[None];retry=[False];last=[time.monotonic()];gap=[0.0];first={};events={};preview=[None]
    settings=AppSettings(str(out/'settings.json'));settings.set('download_path',str(save))
    history=HistoryService(str(out/'history.json'))
    with patch('gui.main_window.AppSettings',return_value=settings),patch('gui.main_window.DownloadHistory',return_value=history),patch('gui.main_window.QMessageBox.question',return_value=QMessageBox.Yes):
        window=MainWindow();window.show();window._manager.configure_workers(1)
        panel=window._settings_panel;d=window._downloader
        original=panel.collect_opts
        def inputs():
            data=original()
            if index[0]>=0 and cases[index[0]][0]=='cookiefile':data['http_headers']={'User-Agent':'B01-test-agent'}
            return data
        panel.collect_opts=inputs
        def start_next():
            index[0]+=1;current[0]=None;retry[0]=False;preview[0]=None
            if index[0]>=len(cases):window.close();return
            name,link,target,opts=cases[index[0]]
            window.navigation.setCurrentRow(0)
            panel.apply_settings({'download_path':str(save),'outtmpl':name+'_%(id)s.%(ext)s','format':'',
                                  'cookiesfrombrowser':'None','cookiefile':'','proxy':'','embed_metadata':False,'embed_chapters':False,**opts})
            d.path.setText(str(save));d.urls._text_edit.setPlainText(link)
            d.urls._btn_formats.click()
        def on_info(link,raw):
            if not d.info:return
            name,_,target,_=cases[index[0]]
            labels=[d.quality.itemText(i) for i in range(d.quality.count())]
            preview[0]={'formats_count':len(raw.get('formats') or []),'quality_options':len(labels)-1,'has_8k':any('4320P' in x for x in labels),
                        'has_60fps_hdr10':any('4320P' in x and '60 FPS' in x and 'HDR10' in x for x in labels)}
            if target=='playlist':
                assert raw.get('_type')=='playlist' and len(raw.get('entries') or [])>0
                preview[0]['playlist_count']=raw.get('playlist_count') or len(raw.get('entries') or [])
                assert d.download.text()=='Download All'
            if target=='metadata':
                assert d.selection.video.height==4320 and d.selection.video.fps==60 and d.selection.video.dynamic_range=='HDR10'
                results.append({'test':name,'preview':preview[0],'status':'metadata-pass','expression':d.selection.yt_dlp_format_expression})
                (out/'ui-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results[-1]),flush=True)
                QTimer.singleShot(50,start_next);return
            if isinstance(target,int):
                profile=window._manager.selection(raw,target).video
                for i in range(1,d.quality.count()):
                    if d.quality.itemData(i).format_id==profile.format_id:d.quality.setCurrentIndex(i);break
                assert d.selection.video.height==target
            elif target=='audio':
                d.audio_only.setChecked(True)
                d.audio_format.setCurrentIndex(d.audio_format.findData('mp3' if name=='audio' else 'best'))
            assert d.download.isEnabled(),d.message.text()
            expected=d.selection
            d.download.click();d.download.click()
            current[0]=window._manager.get_all_tasks()[-1]
            assert current[0].selection==expected
            if name=='8k':assert expected.video.height==4320 and '4320P' in current[0].record.quality
        window._bridge.info_extracted.connect(on_info)
        def preview_failed(link,error):
            results.append({'test':cases[index[0]][0],'status':'preview-failed','error':str(error[1] if isinstance(error,tuple) else error)})
            (out/'ui-results.json').write_text(json.dumps(results,indent=2))
            if hasattr(window,'_error_dialog'):window._error_dialog.reject()
            window.close()
        window._bridge.preview_failed.connect(preview_failed)
        def event(record):
            tid=record['id'];events.setdefault(tid,set()).add(str(record['status']))
            if record['status']==TaskStatus.DOWNLOADING and record.get('downloaded_bytes',0)>0:
                first.setdefault(tid,record.get('downloaded_bytes',0))
                if responsive and current[0] and tid==current[0].id and record.get('downloaded_bytes',0)>1024**2:
                    window._manager.cancel_task(tid)
                if current[0] and tid==current[0].id and cases[index[0]][0]=='4k-resume' and not retry[0] and record.get('downloaded_bytes',0)>.1*(record.get('total_bytes') or 10**15):
                    window._manager.cancel_task(tid)
        window._bridge.task_progress.connect(event);window._bridge.task_updated.connect(event)
        def tick():
            now=time.monotonic();gap[0]=max(gap[0],now-last[0]);last[0]=now
            window.move(40+int(now)%3,40)
            if responsive:window.navigation.setCurrentRow(int(now*5)%5)
            if not current[0] or not current[0].status.terminal:return
            task=current[0];name,_,target,_=cases[index[0]]
            if name=='4k-resume' and task.status==TaskStatus.CANCELLED and not retry[0]:
                retry[0]=True;window._task_table._on_retry(task.id);current[0]=window._manager.get_all_tasks()[-1];return
            r={'test':name,'preview':preview[0],'status':task.status.value,'error':str(task.error) if task.error else None,
               'retry':retry[0],'first_bytes':first.get(task.id),'outputs':task.output_files,'history_rows':window._history_page.table.rowCount(),
               'states':sorted(events.get(task.id,set())),'quality':task.record.quality,'selection_expression':task.selection.yt_dlp_format_expression if task.selection else 'custom',
               'children':len(multiprocessing.active_children())}
            if task.output_files:
                probe=validate_media(task.output_files[0]);(out/(name+'-ffprobe.json')).write_text(json.dumps(probe,indent=2))
                r['streams']=[{k:s.get(k) for k in ('codec_type','width','height','codec_name','pix_fmt','r_frame_rate')} for s in probe['streams']]
                if isinstance(target,int):assert next(s for s in probe['streams'] if s['codec_type']=='video')['height']==target
                if name=='8k':assert next(s for s in probe['streams'] if s['codec_type']=='video')['height']==4320
                if name=='custom':assert next(s for s in probe['streams'] if s['codec_type']=='video')['height']==720
            results.append(r);print(json.dumps(r),flush=True);(out/'ui-results.json').write_text(json.dumps(results,indent=2))
            current[0]=None;QTimer.singleShot(100,start_next)
        timer=QTimer();timer.timeout.connect(tick);timer.start(25)
        QTimer.singleShot(0,start_next);QTimer.singleShot(1200000,window.close)
        last[0]=time.monotonic()
        app.exec();timer.stop();window._manager.shutdown(wait=True)
        summary={'cases':len(results),'children':len(multiprocessing.active_children()),'max_tick_gap':gap[0],
                 'cookie_requests_authenticated':bool(server.requests_seen) and all(r['cookie_ok'] for r in server.requests_seen),
                 'proxy_requests':{k:len(p.records) for k,p in proxies.items()},'proxy_auth':{k:bool(p.records) and all(r['username_ok'] and r['password_ok'] for r in p.records) for k,p in proxies.items()}}
        (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
        assert len(results)==len(cases) and all(r['status'] in (('cancelled',) if responsive else ('completed','metadata-pass')) for r in results)
        if responsive:assert gap[0]<.25 and all(r['first_bytes'] and 'downloading' in r['states'] for r in results)
        assert summary['children']==0
        if not only:assert summary['cookie_requests_authenticated'] and all(summary['proxy_auth'].values())
    for proxy in proxies.values():proxy.close()
    server.close()
    if only and only!='8k':return
    path=next(r['outputs'][0] for r in results if r['test']=='8k')
    with (out/'decode-errors.log').open('wb') as err,(out/'decode-progress.log').open('wb') as log:
        code=subprocess.run(['ffmpeg','-v','error','-stats_period','10','-progress','pipe:1','-i',path,'-fps_mode','passthrough','-enc_time_base:v','demux','-f','null','-'],stdout=log,stderr=err).returncode
    result={'returncode':code,'error_bytes':(out/'decode-errors.log').stat().st_size}
    (out/'decode-result.json').write_text(json.dumps(result));print(json.dumps(result),flush=True)
    assert code==0 and result['error_bytes']==0

if __name__=='__main__':
    multiprocessing.freeze_support();validate(Path(sys.argv[1]).resolve(),sys.argv[2] if len(sys.argv)>2 else None)
