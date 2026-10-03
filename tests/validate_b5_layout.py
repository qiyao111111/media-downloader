"""Real QWidget captures, including simulated display scale and long-title layout."""
import json,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from configs.app_settings import AppSettings
from services.history_service import HistoryService
from gui.main_window import MainWindow
from gui.theme_manager import apply_theme
from app.product_validation import capture
from test_b3_ui import info

out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
app=QApplication([]);settings=AppSettings(str(out/'settings.json'));settings.set('download_path',str(out))
with patch('gui.main_window.AppSettings',return_value=settings),patch('gui.main_window.DownloadHistory',return_value=HistoryService(str(out/'history.json'))):
    w=MainWindow();w.show();d=w._downloader
    d.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=synthetic-layout-only')
    w._on_info_extracted(d.urls.get_first_url(),info(8640,60,'HDR10','中文 Long Title '*120))
    scale=w.devicePixelRatioF();w.resize(int(1366/scale)-20,int(768/scale)-60)
    for theme in ('light','dark','system'):
        apply_theme(app,theme);app.processEvents();rows=capture(w,out/theme,startup=True)
        assert all(r['download_visible'] for r in rows)
        assert w.width()<=1366/scale and w.height()<=768/scale
        assert '8640P' in d.metadata.text()
    w.close();w._manager.shutdown(wait=True)
print(json.dumps({'scale':scale,'physical_target':[1366,768],'logical':[w.width(),w.height()],'themes':3,'languages':2,'pass':True}))
