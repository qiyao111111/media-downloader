"""Qt presentation contracts, independent of source quality and task policy."""
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt,QCoreApplication,QEvent
from PySide6.QtWidgets import QApplication,QLabel,QScrollArea,QLineEdit
from PySide6.QtGui import QPalette
from gui.design_tokens import PALETTES,SPACING,TYPE,CONTROL
from gui.theme_manager import apply_theme
from gui.product_dialogs import ProductDialog
from gui.widgets.presentation import QualityChip,StatusBadge,EmptyStateWidget,RuntimeStatusRow,InfoBanner
from i18n import tr,MISSING_KEYS,CATALOGS
import test_b5_product as fixtures
from test_b3_ui import info
from models.errors import DownloadError


class VisualPolishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    setUp=fixtures.ProductPolishTests.setUp
    def tearDown(self):
        fixtures.ProductPolishTests.tearDown(self)
        self.w.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete);self.app.processEvents()
    ready=fixtures.ProductPolishTests.ready

    def render(self,theme='light'):
        apply_theme(self.app,theme);self.w.show();self.app.processEvents()
        image=self.w.grab().toImage();self.assertFalse(image.isNull());return image

    def chips(self):return [c.text() for c in self.d.findChildren(QualityChip)]

    def test_design_token_contract(self):
        self.assertEqual(SPACING,(4,8,12,16,20,24,32));self.assertEqual(TYPE['page'],24);self.assertEqual(CONTROL['large'],44)
        self.assertEqual(set(PALETTES['light']),set(PALETTES['dark']))

    def test_light_render_and_palette(self):
        self.render();self.assertEqual(self.app.palette().color(QPalette.Base).name(),PALETTES['light']['surface'])
        self.assertNotIn('@',self.app.styleSheet())

    def test_dark_render_and_palette(self):
        self.render('dark');self.assertEqual(self.app.palette().color(QPalette.Text).name(),PALETTES['dark']['text'])
        self.assertIn(PALETTES['dark']['surface'],self.app.styleSheet())

    def test_popup_follows_theme(self):
        self.ready();self.render('dark');self.d.quality.showPopup();self.app.processEvents()
        self.assertEqual(self.d.quality.view().palette().color(QPalette.Base).name(),PALETTES['dark']['surface'])
        self.d.quality.hidePopup();apply_theme(self.app,'light')
        self.assertEqual(self.d.quality.view().palette().color(QPalette.Base).name(),PALETTES['light']['surface'])

    def test_sidebar_selected_icons_and_focus(self):
        self.render();self.w.navigation.setCurrentRow(3)
        self.assertEqual(self.w.pages.currentIndex(),3);self.assertTrue(self.w.navigation.item(3).isSelected())
        for index in range(5):self.assertFalse(self.w.navigation.item(index).icon().isNull())
        self.assertIn('QListWidget::item:focus',self.app.styleSheet())

    def test_downloader_idle_controls(self):
        self.render();self.assertFalse(self.d.download.isEnabled());self.assertFalse(self.d.urls._btn_formats.isEnabled())
        self.assertEqual(self.d.urls._text_edit.height(),44)

    def test_analyzed_selection_not_changed_by_theme(self):
        self.ready();selected=self.d.selection;self.render('dark');self.w._retranslate('zh')
        self.assertEqual(selected,self.d.selection);self.assertEqual(selected.video.height,4320)
        self.assertTrue(self.d.download.isEnabled())

    def test_analyzing_feedback(self):
        self.d.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=test');self.render()
        with patch.object(self.w._manager,'extract_info'):self.d.urls._btn_formats.click()
        self.assertTrue(self.d.urls.spinner.isVisible());self.assertFalse(self.d.urls._btn_formats.isEnabled())
        self.assertEqual(self.d.urls._btn_formats.text(),tr('analyzing'))

    def test_inline_errors_and_retry_action(self):
        self.render()
        with patch('gui.main_window.show_error'):
            for text,key in [('invalid URL','error.invalid_url'),('network failure','error.network'),('HTTP 403','error.403')]:
                self.w._on_info_error('',DownloadError(text));self.assertTrue(self.d.urls._text_edit.property('invalid'))
                self.assertIn(tr(key),self.d.message.text());self.assertFalse(self.d.download.isEnabled())
        self.d.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=test')
        self.assertTrue(self.d.urls._btn_formats.isEnabled());self.assertFalse(self.d.urls._text_edit.property('invalid'))
        self.w._on_info_error('',DownloadError('HTTP 403'));self.assertEqual(self.d.urls._btn_formats.text(),tr('retry'))

    def test_best_quality_recommended(self):
        self.ready();self.render();self.assertTrue(self.d.recommended.isVisible());self.assertEqual(self.d.recommended.text(),tr('recommended'))
        self.d.quality.setCurrentIndex(1);self.assertTrue(self.d.recommended.isHidden())

    def test_8k60_hdr_chips(self):
        self.ready();self.assertEqual(self.chips(),['8K','4320P','60 FPS','AV1','HDR10'])
        old=self.d.findChildren(QualityChip);self.w._retranslate('zh');self.assertTrue(all(chip.isHidden() for chip in old))

    def test_unknown_range_not_mislabeled(self):
        self.d.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=test')
        self.w._on_info_extracted(self.d.urls.get_first_url(),info(4320,60,None))
        self.assertNotIn('SDR',self.chips());self.assertNotIn('HDR',self.chips())

    def test_chip_geometry_consistent(self):
        self.ready();self.render();chips=self.d.findChildren(QualityChip)
        self.assertEqual({c.height() for c in chips},{24});self.assertEqual(len({c.font().pixelSize() for c in chips}),1)
        self.assertEqual(self.d.chips.spacing(),8)

    def add_record(self,status):
        t=self.w._task_table;t.add_task('visual','https://example.invalid',lambda _:None)
        t.update_record({'id':'visual','title':'Title','status':status,'quality':'8K · 4320P','progress':68.18462,'total_bytes':100,'downloaded_bytes':68,'speed':21.4*1024**2,'eta':134})
        return t._table

    def test_queue_downloading_presentation(self):
        t=self.add_record('downloading');self.render();self.w.navigation.setCurrentRow(1);self.app.processEvents()
        self.assertEqual(t.cellWidget(0,3).value(),68);self.assertEqual(t.item(0,4).text(),'21.4 MB/s');self.assertEqual(t.item(0,5).text(),'02:14')
        self.assertEqual(t.cellWidget(0,6).text(),tr('cancel'));self.assertEqual(t.cellWidget(0,2).text(),tr('status.downloading'))
        self.assertIn('8K',t.item(0,1).text());self.assertFalse(t.grab().isNull())

    def test_queue_failed_retry_and_danger(self):
        t=self.add_record('failed');self.assertEqual(t.cellWidget(0,6).text(),tr('retry'))
        self.assertEqual(t.cellWidget(0,2).property('tone'),'danger');self.assertEqual(t.cellWidget(0,3).property('state'),'failed')

    def test_completed_action_and_status(self):
        t=self.add_record('completed');self.assertEqual(t.cellWidget(0,6).text(),tr('open_folder'))
        self.assertEqual(t.cellWidget(0,3).value(),100);self.assertEqual(t.cellWidget(0,2).property('tone'),'success')
        file=self.root/'complete.mp4';file.write_bytes(bytes(1024));self.w._task_table.update_record({'id':'visual','status':'completed','output_path':str(file)})
        self.assertEqual(t.item(0,8).text(),'1.0 KB')

    def test_empty_queue_and_history_icons(self):
        self.assertTrue(self.w._task_table._table.isHidden());self.assertTrue(self.w._history_page.table.isHidden())
        for empty in (self.w._task_table.empty,self.w._history_page.empty):
            self.assertTrue(empty.title.text());self.assertTrue(empty.description.text());self.assertFalse(empty.icon.pixmap().isNull())

    def test_history_terminal_badge_without_data_mutation(self):
        records=[{'task_id':'done','status':'completed','title':'History','url':'url'}];self.w._history_page.render(records)
        self.assertEqual(records[0]['status'],'completed');self.assertEqual(self.w._history_page.table.cellWidget(0,3).property('tone'),'success')
        badge=self.w._history_page.table.cellWidget(0,3);self.w._history_page.render(records)
        self.assertIs(self.w._history_page.table.cellWidget(0,3),badge)

    def test_logs_empty_and_clear_transition(self):
        log=self.w._log_viewer;self.assertFalse(log.empty.icon.pixmap().isNull());log.append('Authorization: SECRET')
        self.assertTrue(log.empty.isHidden());self.assertNotIn('SECRET',log._text_edit.toPlainText())
        log._text_edit.clear();self.assertTrue(log._text_edit.isHidden());self.assertFalse(log.empty.isHidden())

    def test_settings_category_values_preserved(self):
        p=self.w._settings_panel;before=p.collect_opts()
        self.assertEqual(p.categories.count(),7)
        for index,key in enumerate(p.sections):
            p.categories.setCurrentRow(index);self.assertEqual(p.category_pages.currentIndex(),index);self.assertEqual(p.categories.item(index).text(),tr(key))
        self.assertEqual(before,p.collect_opts())

    def test_cookie_badges_and_masked_proxy(self):
        p=self.w._settings_panel
        for browser,key,tone in [('chrome','experimental','warning'),('edge','experimental','warning'),('firefox','best_effort','neutral')]:
            p.cookie_browser_combo.setCurrentIndex(p.cookie_browser_combo.findData(browser));self.assertEqual(p.cookie_badge.text(),tr(key));self.assertEqual(p.cookie_badge.property('tone'),tone)
            self.assertEqual(p.collect_opts()['cookiesfrombrowser'],browser)
        self.assertEqual(p.proxy_edit.echoMode(),QLineEdit.Password);self.assertTrue(p.findChildren(InfoBanner))

    def test_runtime_rows_include_version_and_ready(self):
        self.w._health_ready({'application':{'version':'test'},'ffmpeg':{'status':'READY','version':'r2'},'quickjs':{'status':'NOT_INSTALLED'}})
        rows=self.w.runtime_rows.findChildren(RuntimeStatusRow);self.assertEqual(len(rows),2)
        self.assertEqual(rows[0].badge.text(),tr('runtime.ready'));self.assertEqual(rows[1].badge.property('tone'),'danger')

    def test_about_version_and_icon(self):
        from app.version import VERSION
        self.w.resize(890,452);dialog=ProductDialog(self.w);dialog.show();self.app.processEvents()
        self.assertLessEqual(dialog.height(),self.w.height());self.assertIn(VERSION,dialog.version_label.text())
        self.assertTrue(any(label.pixmap() and not label.pixmap().isNull() for label in dialog.findChildren(QLabel)))

    def language_contract(self,language):
        self.ready();selected=self.d.selection;self.w._retranslate(language);self.render()
        self.assertEqual(self.w._settings_panel.categories.item(0).text(),tr('general'));self.assertEqual(self.d.recommended.text(),tr('recommended'))
        self.assertEqual(self.d.selection,selected);self.assertFalse(MISSING_KEYS)

    def test_zh_render(self):self.language_contract('zh')
    def test_en_render(self):self.language_contract('en')

    def test_new_translation_keys_complete(self):
        keys=('download_title','download_subtitle','configuration','recommended','experimental','best_effort','queue_description','history_description','logs_description','advanced_description','analyze_error_inline','theme_description','language_description')
        for catalog in CATALOGS.values():
            for key in keys:self.assertTrue(catalog[key])

    def test_responsive_action_and_scroll_geometry(self):
        self.ready();self.render()
        for width,height in ((1366,768),(1920,1080),(890,452)):
            self.w.resize(width,height);self.app.processEvents();point=self.d.download.mapTo(self.w,self.d.download.rect().center())
            self.assertTrue(self.w.rect().contains(point));self.assertGreaterEqual(self.d.download.height(),44)
            area=self.w.pages.widget(0).findChild(QScrollArea);self.assertEqual(area.horizontalScrollBar().maximum(),0)

    def test_long_title_and_path_keep_geometry(self):
        title='中文 long title '+('word '*100);self.d.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=test')
        self.w._on_info_extracted(self.d.urls.get_first_url(),info(4320,60,'HDR10',title));self.d.path.setText('中文 path with spaces/'*50);self.render()
        self.assertEqual(self.d.title.toolTip(),title);self.assertLessEqual(self.d.title.height(),self.d.title.fontMetrics().height()*2+4)
        self.assertLess(self.d.path.minimumSizeHint().width(),250)


if __name__=='__main__':unittest.main()
