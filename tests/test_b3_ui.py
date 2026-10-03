"""Qt integration tests without network or added GUI frameworks."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QMessageBox,QLineEdit
from gui.main_window import MainWindow
from gui.error_mapper import error_text
from configs.app_settings import AppSettings
from services.history_service import HistoryService
from models.errors import CookieError,ProxyError,FFmpegError,FormatError,DownloadError,CancelledError
from models.download import TaskStatus
from core.manager import DownloadManager


def info(height=1080,fps=60,range='SDR',title='Test Video'):
    return {'title':title,'channel':'Test Channel','duration':10,'duration_string':'00:10','formats':[
        {'format_id':'v','vcodec':'av01.0.08M.08','acodec':'none','width':height*16//9,'height':height,'fps':fps,'dynamic_range':range,'ext':'mp4','url':'https://example.invalid/v'},
        {'format_id':'a','vcodec':'none','acodec':'opus','abr':130,'ext':'webm','url':'https://example.invalid/a'}]}


class UIIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.settings=AppSettings(str(self.root/'settings.json'));self.settings.set('download_path',str(self.root))
        self.history=HistoryService(str(self.root/'history.json'))
        self.patches=[patch('gui.main_window.AppSettings',return_value=self.settings),patch('gui.main_window.DownloadHistory',return_value=self.history),patch('gui.main_window.show_error')]
        for p in self.patches:p.start()
        self.window=MainWindow();self.d=self.window._downloader
        self.d.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=test')
    def tearDown(self):
        with patch('gui.main_window.QMessageBox.question',return_value=QMessageBox.Yes):self.window.close()
        self.window._manager.shutdown(wait=True)
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()
    def ready(self,data=None):self.window._on_info_extracted(self.d.urls.get_first_url(),data or info())
    def event(self,**kw):
        r={'id':'id1','url':self.d.urls.get_first_url(),'title':'Test','status':'queued','progress':0,**kw}
        self.window._bridge.task_added.emit(r);return r

    def test_analyze_success(self):
        with patch.object(self.window._manager,'extract_info') as call:
            self.d.urls._btn_formats.click();self.assertTrue(self.d.analyzing)
            call.call_args.kwargs['on_result'](self.d.urls.get_first_url(),info())
        self.assertTrue(self.d.download.isEnabled());self.assertIn('Test Channel',self.d.metadata.text())
    def test_analyze_failure(self):
        self.window._on_info_error(self.d.urls.get_first_url(),DownloadError('failed'))
        self.assertFalse(self.d.download.isEnabled());self.assertIn('Analyze failed',self.d.message.text())
    def test_quality_source(self):
        data=info();self.ready(data)
        self.assertEqual(self.d.quality.count(),1+len(self.window._manager.quality_options(data)))
        self.assertEqual(self.d.quality.itemData(1),self.window._manager.quality_options(data)[0])
    def test_best_binding(self):
        self.ready();self.assertEqual(self.d.quality.currentData(),'best')
        self.assertEqual(self.d.selection,self.window._manager.selection(info()))
    def test_8k_render(self):self.ready(info(4320));self.assertIn('8K · 4320P',self.d.quality.itemText(1))
    def test_above_8k_render(self):self.ready(info(8640));self.assertIn('8640P',self.d.quality.itemText(1))
    def test_hdr_render(self):self.ready(info(4320,60,'HDR10'));self.assertIn('HDR10',self.d.quality.itemText(1))
    def test_fps_render(self):self.ready(info(4320,120));self.assertIn('120 FPS',self.d.quality.itemText(1))
    def test_audio_only(self):
        self.ready();self.d.audio_only.setChecked(True)
        self.assertFalse(self.d.quality.isEnabled());self.assertEqual(self.d.selection.mode,'audio')
    def test_download_state(self):
        self.assertFalse(self.d.download.isEnabled());self.ready();self.assertTrue(self.d.download.isEnabled())
        self.d.path.setText(str(self.root/'missing'));self.assertFalse(self.d.download.isEnabled())
    def test_duplicate_click(self):
        self.ready()
        with patch.object(self.window._manager._executor,'submit'):
            self.window._on_download();self.window._on_download()
        self.assertEqual(len(self.window._manager.get_all_tasks()),1)
    def test_progress_event(self):
        r=self.event();self.window._bridge.task_progress.emit({**r,'status':'downloading','progress':50,'speed':2*1024**2,'eta':65,'total_bytes':100,'downloaded_bytes':50})
        t=self.window._task_table._table
        self.assertEqual(t.cellWidget(0,3).value(),50);self.assertEqual(t.item(0,4).text(),'2.0 MB/s');self.assertEqual(t.item(0,5).text(),'01:05')
    def test_completed_event(self):
        r=self.event();self.window._bridge.task_updated.emit({**r,'status':'completed','output_path':str(self.root/'video.mp4')})
        self.assertEqual(self.window._task_table._table.cellWidget(0,6).text(),'Open Folder')
        self.assertEqual(self.window._history_page.table.rowCount(),1)
    def test_failed_event(self):
        r=self.event();self.window._bridge.task_updated.emit({**r,'status':'failed','error':'failed'})
        self.assertEqual(self.window._task_table._table.cellWidget(0,6).text(),'Retry')
    def test_cancelled_event(self):
        r=self.event();self.window._bridge.task_updated.emit({**r,'status':'cancelled'})
        self.assertEqual(self.window._task_table.records['id1']['status'],'cancelled')
    def test_retry(self):
        with patch.object(self.window._manager._executor,'submit'):
            tid=self.window._manager.add_task(self.d.urls.get_first_url(),{})
            self.window._manager.cancel_task(tid)
            self.assertTrue(self.window._retry_url(tid,self.d.urls.get_first_url()))
            self.assertFalse(self.window._retry_url(tid,self.d.urls.get_first_url()))
            self.assertEqual(len(self.window._manager.get_all_tasks()),2)
    def test_queue_add_remove(self):
        self.event();self.window._task_table.delete_task_row('id1');self.assertEqual(self.window._task_table._table.rowCount(),0)
    def test_settings_save_load(self):
        self.window._settings_panel.retries_spin.setValue(4)
        self.assertTrue(self.window._save_settings());loaded=AppSettings(str(self.root/'settings.json'))
        self.assertEqual(loaded.get('retries'),4)
    def test_cookie_path_ui(self):
        p=self.window._settings_panel;p.cookie_file_edit.setText(str(self.root/'cookies.txt'))
        self.assertEqual(p.cookie_file_status.text(),'Configured');self.assertEqual(p.collect_opts()['cookiefile'],str(self.root/'cookies.txt'))
    def test_proxy_masking(self):self.assertEqual(self.window._settings_panel.proxy_edit.echoMode(),QLineEdit.Password)
    def test_empty_queue_cancel_disabled(self):self.assertFalse(self.window._btn_cancel_all.isEnabled())
    def test_netrc_change_invalidates(self):
        self.ready();self.window._settings_panel.cb_netrc.setChecked(True);self.assertIsNone(self.d.info)
    def test_error_mapping(self):
        for error in (CookieError('SID=SECRET'),ProxyError('http://user:SECRET@localhost'),FFmpegError('failed'),FormatError('failed'),CancelledError()):
            message,details=error_text(error);self.assertNotIn('SECRET',details);self.assertTrue(message)
    def test_history_render(self):
        self.history.add('done','https://www.youtube.com/watch?v=test','Title');self.history.update_record('done',status='completed',quality='1080P')
        self.window._load_history();self.assertEqual(self.window._history_page.table.rowCount(),1)
        self.assertEqual(self.window._task_table._table.rowCount(),0)
    def test_stale_preview(self):
        generation=self.window._preview_generation;self.d.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=other')
        self.window._on_info_extracted('https://www.youtube.com/watch?v=test',{**info(),'_ui_request':generation})
        self.assertIsNone(self.d.info)
    def test_auth_change_invalidates(self):
        self.ready();self.window._settings_panel.proxy_edit.setText('http://127.0.0.1:1234');self.assertIsNone(self.d.info)
    def test_unknown_hdr(self):self.ready(info(range='UNKNOWN'));self.assertIn('UNKNOWN',self.d.quality.itemText(1));self.assertNotIn('SDR',self.d.quality.itemText(1))
    def test_no_fake_quality(self):self.ready();self.assertNotIn('8K',' '.join(self.d.quality.itemText(i) for i in range(self.d.quality.count())))
    def test_task_receives_selection(self):
        self.ready(info(4320));selected=self.d.selection
        with patch.object(self.window._manager._executor,'submit'):self.window._on_download()
        task=self.window._manager.get_all_tasks()[0]
        self.assertEqual(task.selection,selected);self.assertEqual(task.ydl_opts['format'],selected.yt_dlp_format_expression)
    def test_container_override(self):
        self.ready();self.d.container.setCurrentIndex(self.d.container.findData('mkv'))
        opts,s=self.window._manager.prepare_download(self.window._inputs(),self.d.info,'best')
        self.assertEqual(opts['merge_output_format'],'mkv');self.assertFalse(any(p.get('key')=='FFmpegVideoConvertor' for p in opts.get('postprocessors',[])))
    def test_postprocessing_view(self):
        r=self.event();self.window._bridge.task_updated.emit({**r,'status':'postprocessing','progress':100})
        self.assertEqual('Post-processing',self.window._task_table._table.item(0,2).text())
        self.assertIn('Merging',self.window._task_table._table.cellWidget(0,3).format())
    def test_indeterminate(self):
        r=self.event();self.window._bridge.task_progress.emit({**r,'status':'downloading','total_bytes':0})
        self.assertEqual(self.window._task_table._table.cellWidget(0,3).maximum(),0)
    def test_playlist_binding(self):
        self.ready({'_type':'playlist','title':'Playlist','entries':[{'id':'a'},{'id':'b'}]})
        self.assertIn('2 videos',self.d.metadata.text());self.assertEqual(self.d.download.text(),'Download Playlist')
        self.assertTrue(self.d.download.isEnabled());self.assertFalse(self.d.quality.isEnabled())
    def test_long_title_and_special(self):
        title=('中文 : ? * " < > | '+('A'*1000));self.ready(info(title=title))
        self.assertEqual(self.d.metadata.textFormat(),Qt.PlainText);self.assertEqual(self.d.metadata.toolTip(),title)
    def test_close_decline(self):
        with patch.object(self.window._manager._executor,'submit'):
            self.window._manager.add_task(self.d.urls.get_first_url(),{})
        self.window.show()
        with patch('gui.main_window.QMessageBox.question',return_value=QMessageBox.No):self.window.close()
        self.assertFalse(self.window._closing)
    def test_experimental_cookie_policy(self):
        p=self.window._settings_panel
        for browser in ('chrome','edge'):
            p.cookie_browser_combo.setCurrentIndex(p.cookie_browser_combo.findData(browser));self.assertIn('Experimental',p.cookie_support.text())
        p.cookie_browser_combo.setCurrentIndex(p.cookie_browser_combo.findData('firefox'));self.assertIn('Best Effort',p.cookie_support.text())
    def test_analyze_duplicate(self):
        with patch.object(self.window._manager,'extract_info') as call:
            self.window._on_list_formats();self.window._on_list_formats();self.assertEqual(call.call_count,1)
    def test_batch_urls(self):
        self.d.urls._text_edit.setPlainText('https://youtu.be/a\nhttps://youtu.be/a\nhttps://youtu.be/b');self.ready()
        with patch.object(self.window._manager._executor,'submit'):self.window._on_download()
        self.assertEqual(len(self.window._manager.get_all_tasks()),2)
    def test_profile_parameter(self):
        p=self.window._settings_panel;p.cookie_browser_combo.setCurrentIndex(p.cookie_browser_combo.findData('firefox'));p.browser_profile_edit.setText('Profile-test')
        self.assertEqual(self.window._build_ydl_opts()['cookiesfrombrowser'],('firefox','Profile-test'))
    def test_custom_format(self):
        self.window._settings_panel.format_combo.setEditText('bv[height<=1080]+ba/b');self.ready()
        self.assertFalse(self.d.quality.isEnabled())
        opts,selection=self.window._manager.prepare_download(self.window._inputs(),self.d.info,'best')
        self.assertEqual(opts['format'],'bv[height<=1080]+ba/b');self.assertIsNone(selection)
    def test_page_navigation_and_ownership(self):
        from PySide6.QtWidgets import QScrollArea
        self.assertIsNone(self.window._settings_dialog.findChild(QScrollArea).widget())
        self.window.show()
        for index in range(5):
            self.window.navigation.setCurrentRow(index);self.app.processEvents()
            self.assertEqual(self.window.pages.currentIndex(),index)
    def test_clear_history_preserves_active(self):
        self.history.add('active','https://youtu.be/a');self.history.add('finished','https://youtu.be/b')
        self.history.update_record('finished',status='completed');self.window._clear_history()
        self.assertEqual([r['task_id'] for r in self.history.list_records()],['active'])
    def test_model_signal_from_worker(self):
        import threading
        r=self.event()
        thread=threading.Thread(target=lambda:self.window._bridge.task_progress.emit({**r,'status':'downloading','progress':25,'total_bytes':100,'downloaded_bytes':25}))
        thread.start();thread.join();self.app.processEvents()
        self.assertEqual(self.window._task_table._table.cellWidget(0,3).value(),25)
    def test_history_open_safe(self):
        path=self.root/'中文 file.mp4';path.write_bytes(b'fixture')
        self.history.add('finished','https://youtu.be/b');self.history.update_record('finished',status='completed',output_path=str(path))
        self.window._load_history();self.window._history_page.table.selectRow(0)
        with patch('gui.history_page.QDesktopServices.openUrl') as open_url:
            self.window._history_page.action('Open Folder')
            self.assertEqual(Path(open_url.call_args.args[0].toLocalFile()),self.root)

if __name__=='__main__':unittest.main()
