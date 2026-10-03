import sys,json,multiprocessing,time
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
if __name__=='__main__':
    multiprocessing.freeze_support()
    from configs.app_settings import AppSettings
    from services.history_service import HistoryService
    from PySide6.QtWidgets import QApplication,QMessageBox,QDialog,QScrollArea
    from gui.main_window import MainWindow
    from gui.theme_manager import apply_theme
    from models.errors import DownloadError
    from i18n import MISSING_KEYS,tr
    app=QApplication([]);settings=AppSettings(str(root/'temp/b51-persistence/settings.json'));history=HistoryService(str(root/'temp/b51-profile/history.json'))
    out=root/'docs/evidence/b5_1';shots=root/'docs/screenshots/b5_1'
    with patch('gui.main_window.AppSettings',return_value=settings),patch('gui.main_window.DownloadHistory',return_value=history):
        w=MainWindow();w.resize(1366,900);w.show();apply_theme(app,settings.get('theme','light'));app.processEvents()
        if sys.argv[1]=='save':
            p=w._settings_panel;p.path_edit.setText(str(root/'temp/b51 final downloads'));p.ffmpeg_path_edit.setText(str(root/'bin'))
            p.theme_combo.setCurrentIndex(p.theme_combo.findData('dark'));p.language_combo.setCurrentIndex(p.language_combo.findData('en'))
            w.navigation.setCurrentRow(3);assert w._save_settings();app.processEvents()
        else:
            assert settings.get('theme')=='dark' and settings.get('language')=='en';assert app.property('theme')=='dark'
            assert w._settings_panel.theme_combo.currentData()=='dark' and w._settings_panel.language_combo.currentData()=='en'
            w.navigation.setCurrentRow(2);app.processEvents();w.grab().save(str(shots/'history-dark.png'));apply_theme(app,'light');app.processEvents();w.grab().save(str(shots/'history.png'));apply_theme(app,'dark')
            def reject():
                for dialog in w.findChildren(QDialog):dialog.reject()
            for text,key in [('network failure','error.network'),('HTTP 403','error.403')]:
                w.navigation.setCurrentRow(0);w._downloader.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=test')
                w._on_info_error('',DownloadError(text));app.processEvents();reject();app.processEvents()
                assert tr(key) in w._downloader.message.text();assert w._downloader.urls._btn_formats.isEnabled()
                w.grab().save(str(shots/('error-'+key.split('.')[-1]+'.png')))
            # A real invalid-input extraction through the Analyze button.
            w._downloader.urls._text_edit.setPlainText('not-a-url');w._downloader.urls._btn_formats.click()
            deadline=time.monotonic()+35
            while w._downloader.analyzing and time.monotonic()<deadline:app.processEvents();time.sleep(.02)
            app.processEvents();reject();assert not w._downloader.analyzing;assert w._downloader.urls._text_edit.property('invalid');assert tr('error.invalid_url') in w._downloader.message.text()
            w.grab().save(str(shots/'error-invalid-url.png'))
            w.navigation.setCurrentRow(4);w._log_viewer._text_edit.clear();app.processEvents();w.grab().save(str(shots/'logs-empty-dark.png'))
            from core.runtime_manager import health
            w._log_viewer.append(json.dumps(health(download_dir=str(root/'temp/b51 final downloads')),indent=2));app.processEvents();w.grab().save(str(shots/'logs-dark.png'));apply_theme(app,'light');app.processEvents();w.grab().save(str(shots/'logs.png'))
            w.navigation.setCurrentRow(0);w._downloader.urls._text_edit.clear()
            for theme in ('light','dark'):
                apply_theme(app,theme);app.processEvents();w.grab().save(str(shots/('downloader-'+theme+'.png')))
            assert not MISSING_KEYS
            (out/'persistence-errors.json').write_text(json.dumps({'separate_process_restart':True,'theme':'dark','language':'en','history_count':len(w._history.list_records()),'invalid_url':'real Analyze extraction','network_failure':'typed-error presentation injection','http_403':'typed-error presentation injection','missing_keys':list(MISSING_KEYS)},indent=2),encoding='utf-8')
        with patch('gui.main_window.QMessageBox.question',return_value=QMessageBox.Yes):w.close()
        w._manager.shutdown(wait=True)
