"""Real Qt layout/DPI checks using synthetic >8K and long-title metadata."""
import json,sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from configs.app_settings import AppSettings
from services.history_service import HistoryService
from gui.main_window import MainWindow

out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
app=QApplication([]);settings=AppSettings(str(out/'settings.json'));settings.set('download_path',str(out))
with patch('gui.main_window.AppSettings',return_value=settings),patch('gui.main_window.DownloadHistory',return_value=HistoryService(str(out/'history.json'))):
    w=MainWindow();w.show();d=w._downloader;rows=[]
    def run():
        scale=w.devicePixelRatioF()
        data={'title':('中文 : ? * " < > | '+ 'Long Title '*100),'duration':10,'channel':'Channel','formats':[
            {'format_id':'v','width':15360,'height':8640,'fps':60,'dynamic_range':'HDR10','vcodec':'av01','acodec':'none','ext':'mp4'},
            {'format_id':'a','vcodec':'none','acodec':'opus','ext':'webm','abr':130}]}
        d.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=synthetic')
        w._on_info_extracted(d.urls.get_first_url(),data)
        for width,height in ((1366,768),(1920,1080)):
            w.resize(int(width/scale)-20,int(height/scale)-60)
            QApplication.processEvents();w.grab().save(str(out/f'{width}x{height}.png'))
            point=d.download.mapTo(w,d.download.rect().center())
            row={'requested_physical':[width,height],'logical':[w.width(),w.height()],'device_pixel_ratio':scale,
                 'download_visible':d.download.isVisible() and w.rect().contains(point),'analyze_enabled':d.urls._btn_formats.isEnabled(),
                 'has_8640':any('8640P' in d.quality.itemText(i) for i in range(d.quality.count()))}
            assert row['download_visible'] and row['has_8640'];rows.append(row)
        for i,name in enumerate(('downloader','queue','history','settings','logs')):
            w.navigation.setCurrentRow(i);QApplication.processEvents();w.grab().save(str(out/(name+'.png')))
        (out/'layout.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True);w.close()
    QTimer.singleShot(100,run);app.exec();w._manager.shutdown(wait=True)
