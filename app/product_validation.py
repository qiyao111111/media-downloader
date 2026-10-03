"""Optional Qt acceptance checks for the existing --validate-release runner."""
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication,QScrollArea
from gui.product_dialogs import ProductDialog
from gui.error_mapper import show_error
from models.errors import CookieError
from i18n import MISSING_KEYS,tr


def capture(window,out,*,startup=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    d=window._downloader;p=window._settings_panel;selection=d.selection
    original_language=p.language_combo.currentData();original_page=window.navigation.currentRow()
    rows=[]
    for language in ('en','zh'):
        window._retranslate(language)
        assert d.selection==selection
        for index,key in enumerate(('download','queue','history','settings','logs')):
            window.navigation.setCurrentRow(index);QApplication.processEvents()
            assert window.pages.currentIndex()==index
            assert window.navigation.item(index).text()==tr('nav.'+key)
            assert window.grab().save(str(out/(language+'-'+key+'.png')))
        if startup:
            window.navigation.setCurrentRow(3)
            area=window.pages.currentWidget().findChild(QScrollArea)
            for key,section in p.sections.items():
                section.set_expanded(True);QApplication.processEvents();area.ensureWidgetVisible(section)
                QApplication.processEvents();window.grab().save(str(out/(language+'-settings-'+key+'.png')))
                section.set_expanded(key=='general')
            for help_mode in (False,True):
                dialog=ProductDialog(window,help_mode=help_mode);dialog.show();QApplication.processEvents()
                dialog.grab().save(str(out/(language+('-help.png' if help_mode else '-about.png'))));dialog.reject()
            show_error(window,CookieError('Chrome DPAPI SID=DO_NOT_LOG'))
            QApplication.processEvents();box=window._error_dialog
            assert 'DO_NOT_LOG' not in box.detailedText()
            box.grab().save(str(out/(language+'-error.png')));box.reject()
            if not window._settings.get('onboarding_complete',False):
                window.show_welcome();QApplication.processEvents()
                window._welcome_dialog.grab().save(str(out/(language+'-welcome.png')));window._welcome_dialog.reject()
        window.navigation.setCurrentRow(0);QApplication.processEvents()
        point=d.download.mapTo(window,d.download.rect().center())
        rows.append({'language':language,'navigation':[window.navigation.item(i).text() for i in range(5)],
                     'quality_labels':[d.quality.itemText(i) for i in range(d.quality.count())],
                     'selection_unchanged':d.selection==selection,'download_visible':d.download.isVisible() and window.rect().contains(point),
                     'logical_size':[window.width(),window.height()],'device_pixel_ratio':window.devicePixelRatioF()})
    window._retranslate(original_language);window.navigation.setCurrentRow(original_page)
    assert not MISSING_KEYS
    (out/'product-ui.json').write_text(json.dumps({'rows':rows,'missing_keys':sorted(MISSING_KEYS)},indent=2,ensure_ascii=False),encoding='utf-8')
    return rows


def startup(window,out,folder):
    prior={'onboarding_complete':window._settings.get('onboarding_complete',False),
           'language':window._settings.get('language'),'download_folder':window._settings.get('download_path'),
           'history_count':len(window._history.list_records())}
    capture(window,out,startup=True)
    # Use the actual first-launch save action, not a parallel settings writer.
    if not prior['onboarding_complete']:
        window.show_welcome();welcome=window._welcome_dialog
        welcome.language.setCurrentIndex(welcome.language.findData('zh'));welcome.path.setText(folder);welcome.save()
        assert window._settings.get('onboarding_complete')
    p=window._settings_panel;p.language_combo.setCurrentIndex(p.language_combo.findData('zh'))
    p.path_edit.setText(folder);p.theme_combo.setCurrentIndex(p.theme_combo.findData('system'))
    assert window._save_settings()
    prior['saved_onboarding_complete']=window._settings.get('onboarding_complete')
    (Path(out)/'startup.json').write_text(json.dumps(prior,indent=2,ensure_ascii=False),encoding='utf-8')
