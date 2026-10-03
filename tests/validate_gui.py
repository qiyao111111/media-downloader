"""Windows GUI responsiveness and exit check using real Qt and loopback media."""

import json
import multiprocessing
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from configs.app_settings import AppSettings
from core.history import DownloadHistory
from gui.main_window import MainWindow
from loopback import MediaServer


def validate(out):
    app=QApplication([]);out.mkdir(parents=True,exist_ok=True)
    fixture=out/'fixture.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=320x180:rate=25',
                    '-f','lavfi','-i','sine=frequency=440','-t','6','-c:v','libx264','-c:a','aac',str(fixture)],check=True)
    server=MediaServer(fixture,slow=True)
    with patch('gui.main_window.AppSettings',return_value=AppSettings(str(out/'settings.json'))), \
         patch('gui.main_window.DownloadHistory',return_value=DownloadHistory(str(out/'history.json'))), \
         patch('gui.main_window.FormatPreviewDialog.exec',return_value=0):
        w=MainWindow();w.show()
        panel=w._settings_dialog.settings_panel
        panel.format_combo.setEditText('b');panel.path_edit.setText(str(out));panel.remux_combo.setCurrentText('mkv')
        w._url_input._text_edit.setPlainText(f'http://127.0.0.1:{server.server_address[1]}/fixture.mp4')
        collect=panel.collect_opts;stage=['preview'];last=[time.monotonic()];gaps=[];ticks={};pp=[]
        def options():
            opts=collect();opts['postprocessor_args']={'videoremuxer+ffmpeg_i':['-readrate','1']}
            opts['postprocessor_hooks']=[lambda d:pp.append((d.get('postprocessor'),d.get('status')))]
            return opts
        panel.collect_opts=options
        def info_received(url,info):
            stage[0]='download';w._on_download()
        w._bridge.info_extracted.connect(info_received)
        def tick():
            now=time.monotonic();gaps.append(now-last[0]);last[0]=now
            ticks[stage[0]]=ticks.get(stage[0],0)+1
            w.move(40+ticks[stage[0]]%3,40)
            if pp and pp[-1]==('VideoRemuxer','started'):stage[0]='postprocess'
            if ticks.get(stage[0],0)==3:
                w._settings_dialog.show();QTimer.singleShot(50,w._settings_dialog.hide)
            tasks=w._manager.get_all_tasks()
            if tasks and tasks[0].status.value=='completed' and stage[0] not in ('cancel','exit'):
                stage[0]='cancel';w._on_download();QTimer.singleShot(200,w._btn_cancel_all.click)
            if len(tasks)>1 and tasks[-1].status.value=='cancelled' and stage[0]!='exit':
                stage[0]='exit';w._on_list_formats();QTimer.singleShot(10,w.close)
            if now-start>25:w.close()
        timer=QTimer();timer.timeout.connect(tick);timer.start(20)
        start=time.monotonic();QTimer.singleShot(0,w._on_list_formats)
        app.exec();timer.stop();w._manager.shutdown(wait=True)
        result={'test':'gui-preview-download-postprocessing-exit','ticks':ticks,'max_tick_gap':max(gaps),
                'completed':any(t.status.value=='completed' for t in w._manager.get_all_tasks()),
                'cancelled':any(t.status.value=='cancelled' for t in w._manager.get_all_tasks()),
                'worker_children_after_exit':len(multiprocessing.active_children()),'elapsed':time.monotonic()-start}
        print(json.dumps(result),flush=True)
        (out/'gui-results.json').write_text(json.dumps(result),encoding='utf-8')
        assert result['completed'] and result['cancelled'] and ticks.get('postprocess',0)>=2 and result['max_tick_gap']<1
        assert result['worker_children_after_exit']==0
    server.close()


if __name__=='__main__':
    multiprocessing.freeze_support();validate(Path(sys.argv[1]).resolve())
