"""Real lifecycle and GUI responsiveness, with an active exit and safe filename."""
import json,multiprocessing,subprocess,sys,time
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QMessageBox
from configs.app_settings import AppSettings
from services.history_service import HistoryService
from gui.main_window import MainWindow
from loopback import MediaServer


def validate(out):
    out.mkdir(parents=True,exist_ok=True);fixture=out/'fixture.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=1280x720:rate=25','-f','lavfi','-i','sine=frequency=440','-t','6','-c:v','libx264','-preset','ultrafast','-c:a','aac',str(fixture)],check=True)
    server=MediaServer(fixture,slow=True);app=QApplication([]);settings=AppSettings(str(out/'settings.json'));settings.set('download_path',str(out))
    history=HistoryService(str(out/'history.json'));stage=['first'];current=[None];ticks={};last=[time.monotonic()];gap=[0.0];states=[];visited=set()
    with patch('gui.main_window.AppSettings',return_value=settings),patch('gui.main_window.DownloadHistory',return_value=history),patch('gui.main_window.QMessageBox.question',return_value=QMessageBox.Yes):
        w=MainWindow();w.show();d=w._downloader;p=w._settings_panel;original=p.collect_opts
        def inputs():
            data=original();data['postprocessor_args']={'videoremuxer+ffmpeg_i':['-readrate','1']};return data
        p.collect_opts=inputs
        def start():
            p.apply_settings({'format':'b','download_path':str(out),'outtmpl':stage[0]+'_%(title)s.%(ext)s','remux_video':'mkv','embed_metadata':False,'embed_chapters':False})
            d.path.setText(str(out));d.urls._text_edit.setPlainText(f'http://127.0.0.1:{server.server_address[1]}/Chinese_%E4%B8%AD%E6%96%87_%3A%3F%2A%22%3C%3E%7C.mp4')
            w._on_list_formats()
        def ready(url,info):
            d.download.click();current[0]=w._manager.get_all_tasks()[-1]
            if stage[0]=='cancel':QTimer.singleShot(150,lambda:w._manager.cancel_task(current[0].id))
            if stage[0]=='exit':QTimer.singleShot(80,w.close)
        w._bridge.info_extracted.connect(ready)
        def record(r):states.append(r['status'])
        w._bridge.task_updated.connect(record)
        def tick():
            now=time.monotonic();gap[0]=max(gap[0],now-last[0]);last[0]=now;ticks[stage[0]]=ticks.get(stage[0],0)+1
            index=ticks[stage[0]]%5;w.navigation.setCurrentRow(index);visited.add(index);w.move(40+index,40)
            if current[0] and current[0].status.terminal:
                if stage[0]=='first':
                    assert current[0].status.value=='completed';stage[0]='cancel';current[0]=None;QTimer.singleShot(0,start)
                elif stage[0]=='cancel':
                    assert current[0].status.value=='cancelled';stage[0]='exit';current[0]=None;QTimer.singleShot(0,start)
        timer=QTimer();timer.timeout.connect(tick);timer.start(25);QTimer.singleShot(0,start);QTimer.singleShot(120000,w.close)
        # Measure the running event loop, excluding widget construction before exec().
        last[0]=time.monotonic()
        app.exec();timer.stop();w._manager.shutdown(wait=True)
        completed=next(t for t in w._manager.get_all_tasks() if t.status.value=='completed')
        filename=Path(completed.output_files[0]).name
        assert not any(c in filename for c in ':?*"<>|')
        result={'stages':ticks,'visited_pages':sorted(visited),'states':[str(s) for s in states],
                'max_tick_gap':gap[0],'children':len(multiprocessing.active_children()),'safe_filename':filename,
                'completed':True,'cancelled':True,'active_exit':stage[0]=='exit'}
        (out/'lifecycle.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
        assert gap[0]<.25 and len(visited)==5 and result['children']==0 and result['active_exit']
    server.close()

if __name__=='__main__':multiprocessing.freeze_support();validate(Path(sys.argv[1]).resolve())
