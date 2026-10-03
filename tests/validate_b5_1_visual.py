import sys,json,time,multiprocessing
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root));sys.path.insert(0,str(root/'tests'))
if __name__=='__main__':
    multiprocessing.freeze_support()
    from PySide6.QtWidgets import QApplication,QMessageBox,QScrollArea
    from configs.app_settings import AppSettings
    from services.history_service import HistoryService
    from gui.main_window import MainWindow
    from gui.theme_manager import apply_theme
    from gui.product_dialogs import ProductDialog
    from test_b3_ui import info
    from i18n import MISSING_KEYS
    app=QApplication([]);scale=app.primaryScreen().devicePixelRatio()
    out=root/'build/b51-visual'/str(scale);out.mkdir(parents=True,exist_ok=True)
    settings=AppSettings(str(root/'temp/b51-visual/settings.json'));settings.update_from({'download_path':str(root/'temp/b51 downloads'),'onboarding_complete':True,'ffmpeg_location':str(root/'bin')})
    history=HistoryService(str(root/'temp/b51-visual/history.json'))
    results=[]
    with patch('gui.main_window.AppSettings',return_value=settings),patch('gui.main_window.DownloadHistory',return_value=history):
        w=MainWindow();w.show()
        for language in ('en','zh'):
            w._retranslate(language)
            for theme in ('light','dark'):
                apply_theme(app,theme)
                for width,height in ((1366,768),(1920,1080)):
                    # Physical desktop minus native window frame/taskbar allowance.
                    logical=(int((width-20)/scale),int((height-60)/scale));w.resize(*logical)
                    prefix=f'{language}-{theme}-{width}'
                    d=w._downloader;d.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=test');w._on_info_extracted(d.urls.get_first_url(),info(4320,60,'HDR10','中文 Long title '+('word '*90)))
                    app.processEvents()
                    for index,name in enumerate(('downloader','queue','history','settings','logs')):
                        w.navigation.setCurrentRow(index);app.processEvents()
                        if index==3:
                            for category in range(7):
                                w._settings_panel.categories.setCurrentRow(category);app.processEvents();assert w.pages.widget(3).findChild(QScrollArea).horizontalScrollBar().maximum()==0;w.grab().save(str(out/f'{prefix}-settings-{category}.png'))
                        else:w.grab().save(str(out/f'{prefix}-{name}.png'))
                        if index==1:
                            t=w._task_table;t.add_task('layout','https://example.invalid',lambda _:None);t.update_record({'id':'layout','title':'Long Chinese 中文 title example','status':'downloading','quality':'8K · 4320P · 60 FPS · AV1 · HDR10','progress':68.18462,'speed':21.4*1024**2,'eta':134,'downloaded_bytes':68,'total_bytes':100});app.processEvents();w.grab().save(str(out/f'{prefix}-queue-active.png'));assert t._table.horizontalScrollBar().maximum()==0;t.delete_task_row('layout')
                    w.navigation.setCurrentRow(0);app.processEvents()
                    area=w.pages.widget(0).findChild(QScrollArea)
                    assert area.horizontalScrollBar().maximum()==0,(prefix,'downloader overflow',area.horizontalScrollBar().maximum())
                    assert d.download.height()>=44,(prefix,d.download.height())
                    assert w.rect().contains(d.download.mapTo(w,d.download.rect().center()))
                    dialog=ProductDialog(w);dialog.show();app.processEvents();dialog.grab().save(str(out/f'{prefix}-about.png'));assert dialog.width()<logical[0];assert dialog.height()<=logical[1];dialog.reject()
                    d.quality.showPopup();app.processEvents();d.quality.view().window().grab().save(str(out/f'{prefix}-quality-popup.png'));d.quality.hidePopup()
                    menu=w.menuBar().actions()[0].menu();menu.popup(w.menuBar().mapToGlobal(w.menuBar().rect().bottomLeft()));app.processEvents();menu.grab().save(str(out/f'{prefix}-menu.png'));menu.hide()
                    results.append({'case':prefix,'physical_desktop':[width,height],'logical_client':[w.width(),w.height()],'scale':scale,'download_button_height':d.download.height(),'horizontal_overflow':area.horizontalScrollBar().maximum()})
        assert not MISSING_KEYS,MISSING_KEYS
        with patch('gui.main_window.QMessageBox.question',return_value=QMessageBox.Yes):w.close()
        w._manager.shutdown(wait=True)
    (out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
