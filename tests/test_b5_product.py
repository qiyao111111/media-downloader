"""RC presentation contracts; no replacement business logic or network fixtures."""
import hashlib,json,re,string,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication,QMessageBox,QLineEdit,QPushButton
from app.version import PRODUCT,VERSION,WINDOWS_VERSION
from configs.app_settings import AppSettings
from services.history_service import HistoryService
from gui.main_window import MainWindow
from gui.product_dialogs import ProductDialog,WelcomeDialog,open_licenses
from gui.error_mapper import error_key,error_text
from i18n import CATALOGS,MISSING_KEYS,tr,set_language,runtime_label
from models.errors import CookieError,AuthenticationError,ProxyError,FFmpegError,FormatError,CancelledError,DownloadError
from test_b3_ui import info

ROOT=Path(__file__).resolve().parents[1]


class ProductPolishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.settings=AppSettings(str(self.root/'settings.json'));self.settings.set('download_path',str(self.root))
        self.history=HistoryService(str(self.root/'history.json'))
        self.patches=[patch('gui.main_window.AppSettings',return_value=self.settings),patch('gui.main_window.DownloadHistory',return_value=self.history)]
        for p in self.patches:p.start()
        self.w=MainWindow();self.p=self.w._settings_panel;self.d=self.w._downloader
    def tearDown(self):
        for dialog in self.w.findChildren(__import__('PySide6.QtWidgets',fromlist=['QDialog']).QDialog):dialog.reject()
        with patch('gui.main_window.QMessageBox.question',return_value=QMessageBox.Yes):self.w.close()
        self.w._manager.shutdown(wait=True)
        for p in reversed(self.patches):p.stop()
        set_language('en');MISSING_KEYS.clear();self.tmp.cleanup()
    def ready(self):
        self.d.urls._text_edit.setPlainText('https://www.youtube.com/watch?v=test')
        self.w._on_info_extracted(self.d.urls.get_first_url(),info(4320,60,'HDR10'))

    def test_version_single_source_and_about(self):
        self.assertRegex(VERSION,r'^0\.9\.0-rc2$');self.assertEqual(WINDOWS_VERSION,(0,9,0,2))
        dialog=ProductDialog(self.w);self.assertIn(VERSION,dialog.version_label.text())
        self.assertEqual(self.w.windowTitle(),PRODUCT)
        import build_windows
        build_windows.metadata_files()
        metadata=(ROOT/'build/version.txt').read_text(encoding='utf-8')
        self.assertIn("'ProductVersion', '"+VERSION+"'",metadata)

    def test_catalog_keys_and_placeholders_complete(self):
        self.assertEqual(set(CATALOGS['zh_CN']),set(CATALOGS['en_US']))
        for key,en in CATALOGS['en_US'].items():
            zh=CATALOGS['zh_CN'][key];self.assertTrue(en and zh,key)
            fields=lambda text:{f for _,f,_,_ in string.Formatter().parse(text) if f}
            self.assertEqual(fields(en),fields(zh),key)

    def test_missing_key_never_reaches_user(self):
        with self.assertLogs('desktop',level='WARNING'):
            self.assertEqual(tr('not.registered'),tr('error.generic'))
        self.assertIn('not.registered',MISSING_KEYS)

    def test_language_switch_covers_bound_pages_and_controls(self):
        self.assertTrue(self.w._save_settings());self.ready();selection=self.d.selection
        for language in ('zh','en'):
            self.w._retranslate(language)
            self.assertEqual(self.w.navigation.item(0).text(),tr('nav.download'))
            self.assertEqual(self.d.download.text(),tr('download'))
            self.assertEqual(self.d.selection,selection)
            for obj in [self.w,*self.w.findChildren(QObject)]:
                for method,(key,values) in (obj.property('i18n_bindings') or {}).items():
                    getter={'setText':'text','setTitle':'title','setWindowTitle':'windowTitle','setPlaceholderText':'placeholderText','setToolTip':'toolTip','showMessage':'currentMessage'}[method]
                    if obj is self.w._log_viewer.legend:continue
                    self.assertEqual(getattr(obj,getter)(),tr(key,**values),key)
        self.assertFalse(MISSING_KEYS)

    def test_translation_does_not_change_core_inputs(self):
        self.ready();self.p.cookie_browser_combo.setCurrentIndex(self.p.cookie_browser_combo.findData('firefox'))
        self.p.browser_profile_edit.setText('Profile 1');self.p.proxy_edit.setText('socks5h://localhost:1080')
        before=self.w._build_ydl_opts()
        self.w._retranslate('zh');after=self.w._build_ydl_opts()
        # The builder creates fresh functools.partial callbacks on every call.
        for opts in (before,after):
            opts['retry_sleep_functions']={key:(value.func,value.args,value.keywords) for key,value in opts['retry_sleep_functions'].items()}
        self.assertEqual(before,after)
        self.assertEqual(after['cookiesfrombrowser'],('firefox','Profile 1'))

    def test_status_labels_and_merge_progress(self):
        table=self.w._task_table;table.add_task('id','url',lambda _:None)
        record={'id':'id','status':'postprocessing','quality':'8K · 4320P · 60 FPS · AV1 · HDR10','progress':100}
        table.update_record(record);self.w._retranslate('zh')
        self.assertEqual(table.records['id']['status'],'postprocessing')
        self.assertEqual(table._table.item(0,2).text(),tr('status.postprocessing'))
        self.assertEqual(table._table.cellWidget(0,3).format(),tr('merging'))
        self.assertEqual(table._table.cellWidget(0,3).maximum(),0)

    def test_codec_hint_uses_core_family_without_changing_selection(self):
        self.ready();selected=self.d.selection
        self.assertIn(tr('codec_warning'),self.d.message.text())
        self.assertEqual(self.d.selection,selected)
        self.d.quality.setCurrentIndex(1)
        self.assertIn(tr('codec_compatibility'),self.d.message.text())

    def test_error_messages_and_details_are_safe(self):
        errors=[(DownloadError('invalid URL'),'error.invalid_url'),(DownloadError('video unavailable'),'error.unavailable'),
                (AuthenticationError('login required'),'error.auth'),(CookieError('Chrome DPAPI SID=SECRET'),'error.cookies'),
                (CookieError('cookies.txt malformed'),'error.cookie_file'),(ProxyError('http://u:SECRET@host'),'error.proxy'),
                (FormatError('no format'),'error.format'),(FFmpegError('required'),'error.ffmpeg_missing'),
                (FFmpegError('merge failed'),'error.merge'),(DownloadError('Not enough disk space'),'error.disk'),
                (DownloadError('network failure'),'error.network'),(DownloadError('YouTube challenge'),'error.challenge'),
                (DownloadError('HTTP 403'),'error.403'),(CancelledError(),'error.cancelled')]
        for language in ('en','zh'):
            set_language(language)
            for error,key in errors:
                message,details=error_text(error)
                self.assertEqual(error_key(error),key);self.assertEqual(message,tr(key))
                self.assertNotIn('SECRET',details);self.assertNotIn('Traceback',message)

    def test_runtime_labels_and_actual_version(self):
        self.w._retranslate('zh')
        self.w._health_ready({'application':{'status':'READY','version':VERSION,'os':'Windows test','architecture':'AMD64'},
                             'quickjs':{'status':'READY','version':'0.17.0'},'ffmpeg':{'status':'NOT_INSTALLED','version':'--'}})
        self.assertIn(VERSION,self.w._runtime_label.text());self.assertIn(runtime_label('READY'),self.w._runtime_label.text())
        self.assertIn(runtime_label('NOT_INSTALLED'),self.w._runtime_label.text());self.assertNotIn('READY',self.w._runtime_label.text())

    def test_experimental_cookie_labels_preserve_browser_values(self):
        self.w._retranslate('zh')
        for browser in ('chrome','edge','firefox'):
            self.p.cookie_browser_combo.setCurrentIndex(self.p.cookie_browser_combo.findData(browser))
            self.assertEqual(self.p.cookie_support.text(),tr('browser.'+browser))
            self.assertEqual(self.p.collect_opts()['cookiesfrombrowser'],browser)
        self.assertEqual(self.p.proxy_edit.echoMode(),QLineEdit.Password)

    def test_first_launch_saves_language_and_folder(self):
        welcome=WelcomeDialog(self.w);welcome.language.setCurrentIndex(welcome.language.findData('zh'));welcome.path.setText(str(self.root))
        welcome.save();saved=AppSettings(str(self.root/'settings.json'))
        self.assertTrue(saved.get('onboarding_complete'));self.assertEqual(saved.get('language'),'zh')
        self.assertEqual(saved.get('download_path'),str(self.root))

    def test_rc_status_and_local_help(self):
        for language in ('en','zh'):
            set_language(language);dialog=ProductDialog(self.w,help_mode=True)
            text='\n'.join(label.text() for label in dialog.findChildren(__import__('PySide6.QtWidgets',fromlist=['QLabel']).QLabel))
            self.assertIn(tr('rc'),text);self.assertIn(tr('help_steps'),text);self.assertNotIn('Stable',text)

    def test_history_confirmation_and_log_view_clear(self):
        self.history.add('done','url');self.history.update_record('done',status='completed')
        with patch('gui.main_window.QMessageBox.question',return_value=QMessageBox.No):self.w._confirm_clear_history()
        self.assertEqual(len(self.history.list_records()),1)
        log=self.root/'log.txt';log.write_text('retained')
        self.w._log_viewer.append('Authorization: SECRET');self.w._log_viewer.copy_logs()
        self.assertNotIn('SECRET',self.app.clipboard().text());self.w._log_viewer._text_edit.clear()
        self.assertEqual(log.read_text(),'retained')

    def test_license_entry_opens_local_notices(self):
        with patch('gui.product_dialogs.QDesktopServices.openUrl') as opened:
            open_licenses(self.w);self.assertTrue(opened.call_args.args[0].isLocalFile())

    def test_portable_readme_notices_sources_and_translations_packaged(self):
        with zipfile.ZipFile(ROOT/'dist/release/MediaDownloader-Portable.zip') as archive:
            names=set(archive.namelist());prefix='MediaDownloader-Portable/'
            readme=archive.read(prefix+'README.txt').decode('utf-8')
            self.assertIn(VERSION,readme);self.assertIn('请勿分享',readme);self.assertIn('Do not share',readme)
            self.assertIn(prefix+'THIRD_PARTY_NOTICES.txt',names)
            for path in ('i18n/en_US.json','i18n/zh_CN.json','PySide6/translations/qtbase_zh_CN.qm'):
                self.assertIn(prefix+'_internal/'+path,names)
            self.assertTrue(any('/licenses/' in n for n in names));self.assertTrue(any('/SOURCES/' in n for n in names))

    def test_release_manifest_identity_and_hashes(self):
        release=ROOT/'dist/release';data=json.loads((release/'release-manifest.json').read_text())
        self.assertEqual(data['product'],PRODUCT);self.assertEqual(data['version'],VERSION);self.assertRegex(data['build_commit'],r'^[0-9a-f]{40}$')
        for name,key in (('MediaDownloader-Portable.zip','portable_sha256'),('MediaDownloader-Setup.exe','installer_sha256')):
            with (release/name).open('rb') as file:self.assertEqual(hashlib.file_digest(file,'sha256').hexdigest(),data[key])
        self.assertEqual(data['clean_machine_gate'],'NOT TESTED');self.assertEqual(data['public_distribution_gate'],'NEEDS LEGAL REVIEW')
        self.assertFalse(any(word in data for word in ('cookiefile','proxy','user_path')))


if __name__=='__main__':unittest.main()
