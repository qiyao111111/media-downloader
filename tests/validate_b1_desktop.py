"""Explicit full GUI smoke: 1080p/4K/MP3, cancel+retry/resume, cookies/proxies."""
import json
import multiprocessing
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from configs.app_settings import AppSettings
from core.history import DownloadHistory
from core.ffmpeg_utils import validate_media
from gui.main_window import MainWindow
from models.download import TaskStatus
from loopback import MediaServer, Proxy, USER, PASSWORD


def validate(out, dynamic=False, only=None):
    out.mkdir(parents=True, exist_ok=True)
    fixture=out/'fixture.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=320x180:rate=25',
                    '-f','lavfi','-i','sine=frequency=440','-t','3','-c:v','libx264','-c:a','aac',str(fixture)],check=True)
    server=MediaServer(fixture, require_cookie=True)
    cookiefile=out/'controlled-cookies.txt'
    cookiefile.write_text('# Netscape HTTP Cookie File\n127.0.0.1\tFALSE\t/\tFALSE\t2147483647\taudit_session\tcontrolled-test\n')
    proxies={s:Proxy(socks=s!='http') for s in ('http','socks5','socks5h')}
    url='https://www.youtube.com/watch?v=E86EwGT_c2M'
    cases=[('1080p',url,{'format':'bv[height<=1080]+ba','merge_output_format':'mp4'}),
           ('4k-cancel-retry',url,{'format':'bv[height=2160]+ba','merge_output_format':'mp4'}),
           ('audio',url,{'format':'ba','extract_audio':True,'audio_format':'mp3'}),
           ('cookiefile',f'http://127.0.0.1:{server.server_address[1]}/fixture.mp4',{'format':'b','cookiefile':str(cookiefile)})]
    for scheme, proxy in proxies.items():
        endpoint=f'{scheme}://{quote(USER.decode())}:{quote(PASSWORD.decode())}@127.0.0.1:{proxy.server_address[1]}'
        cases.append((scheme,url,{'format':'ba','proxy':endpoint}))
    if dynamic:
        cases[0][2].update(format='', quality_target=1080)
        cases[1][2].update(format='', quality_target=2160)
        for name, _, options in cases:
            if name in ('audio', 'http', 'socks5', 'socks5h'):
                options.update(format='', quality_target='audio')
        cases.append(('custom', url, {'format': 'ba'}))
    if only:
        cases = [case for case in cases if case[0] == only]
    app=QApplication([]);results=[];index=[-1];current=[None];last=[time.monotonic()];gap=[0];first={};retried=[False];preview=[False]
    history=DownloadHistory(str(out/'history.json'));settings=AppSettings(str(out/'settings.json'))
    with patch('gui.main_window.AppSettings',return_value=settings),patch('gui.main_window.DownloadHistory',return_value=history), \
         patch('gui.main_window.FormatPreviewDialog.exec',return_value=0):
        window=MainWindow();window.show();window._manager.configure_workers(1)
        panel=window._settings_dialog.settings_panel;collect=panel.collect_opts
        def inputs():
            data=collect()
            if index[0]>=0 and cases[index[0]][0]=='cookiefile':data['http_headers']={'User-Agent':'B01-test-agent'}
            return data
        panel.collect_opts=inputs
        def start_next():
            index[0]+=1;current[0]=None;retried[0]=False;preview[0]=False
            if index[0]>=len(cases):window.close();return
            name, link, options=cases[index[0]]
            panel.apply_settings({'download_path':str(out),'outtmpl':name+'_%(id)s.%(ext)s',
                                  'cookiesfrombrowser':'None','cookiefile':'','proxy':'',**options})
            window._url_input._text_edit.setPlainText(link)
            window._on_list_formats()
        def on_info(link, info):
            preview[0]=True;window._btn_download.click()
            current[0]=window._manager.get_all_tasks()[-1]
        window._bridge.info_extracted.connect(on_info)
        def on_progress(tid, data):
            if data.get('status')=='downloading':first.setdefault(tid,data.get('downloaded_bytes',0))
            if current[0] and tid==current[0].id and cases[index[0]][0]=='4k-cancel-retry' and not retried[0]:
                total=data.get('total_bytes') or 10**15
                if data.get('downloaded_bytes',0)>.1*total:window._manager.cancel_task(tid)
        window._bridge.progress.connect(on_progress)
        def tick():
            now=time.monotonic();gap[0]=max(gap[0],now-last[0]);last[0]=now
            if not current[0] or not current[0].status.terminal:return
            task=current[0];name,_,_=cases[index[0]]
            if name=='4k-cancel-retry' and task.status==TaskStatus.CANCELLED and not retried[0]:
                retried[0]=True;window._task_table._on_retry(task.id);current[0]=window._manager.get_all_tasks()[-1];return
            row={'test':name,'preview':preview[0],'status':task.status.value,'error':str(task.error) if task.error else None,
                 'retry':retried[0],'first_download_bytes':first.get(task.id),'outputs':task.output_files,'children':len(multiprocessing.active_children())}
            if task.output_files:
                probe=validate_media(task.output_files[0]);row['streams']=[{k:s.get(k) for k in ('codec_type','width','height','codec_name')} for s in probe['streams']]
            results.append(row);print(json.dumps(row),flush=True)
            (out/'desktop-results.json').write_text(json.dumps(results,indent=2))
            current[0]=None;QTimer.singleShot(100,start_next)
        timer=QTimer();timer.timeout.connect(tick);timer.start(20)
        QTimer.singleShot(0,start_next);QTimer.singleShot(600000,window.close)
        app.exec();timer.stop();window._manager.shutdown(wait=True)
        final={'max_tick_gap':gap[0],'cases':len(results),'children':len(multiprocessing.active_children()),'history_count':len(history.list_records())}
        (out/'desktop-summary.json').write_text(json.dumps(final));print(json.dumps(final),flush=True)
        assert len(results)==len(cases) and all(r['preview'] and r['status']=='completed' for r in results)
        for result in results:
            if result['test'] == '4k-cancel-retry':
                assert result['retry'] and result['first_download_bytes']>0
        assert final['children']==0 and gap[0]<1
    for proxy in proxies.values():proxy.close()
    server.close()


if __name__=='__main__':
    multiprocessing.freeze_support()
    only = sys.argv[sys.argv.index('--only')+1] if '--only' in sys.argv else None
    validate(Path(sys.argv[1]).resolve(), '--dynamic' in sys.argv, only)
