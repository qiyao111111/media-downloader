"""Offline regression checks: python -m unittest discover -s tests -v."""

import json
import pickle
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import yt_dlp
from PySide6.QtWidgets import QApplication

from configs.app_settings import AppSettings
from configs.presets import PresetManager, BUILTIN_PRESETS
from configs.ydl_opts import build_opts
from core.credentials import persistent_options, persistent_url, redact, validate_cookie_file
from core.runtime import DownloadCancelled, _job
from core.task import DownloadTask, TaskStatus
from core.manager import DownloadManager
from gui.main_window import MainWindow


class Connection:
    def __init__(self):
        self.messages = []

    def send(self, value):
        self.messages.append(value)

    def close(self):
        pass


class CoreChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_option_types_and_api(self):
        self.assertEqual(build_opts()['proxy'], '')
        opts = build_opts({'ratelimit': '50K', 'min_filesize': '2M', 'max_filesize': '1G',
                           'buffersize': '16K', 'http_chunk_size': '1M', 'retries': '2',
                           'fragment_retries': '3', 'concurrent_fragment_downloads': '4',
                           'socket_timeout': '10.5', 'sleep_interval': '1', 'max_sleep_interval': '2',
                           'playliststart': '1', 'playlistend': '3', 'match_filter': 'duration>60',
                           'date_range_start': '20260101', 'date_range_end': '20261001'})
        self.assertEqual(opts['ratelimit'], 51200)
        self.assertIsInstance(opts['fragment_retries'], int)
        self.assertEqual(opts['retry_sleep_functions']['http'](3), 3)
        self.assertEqual(opts['retry_sleep_functions']['http'](n=3), 3)
        self.assertIsNone(opts['match_filter']({'duration': 120}, incomplete=False))
        self.assertIsNotNone(opts['match_filter']({'duration': 20}, incomplete=False))
        self.assertIn('20260601', opts['daterange'])
        self.assertNotIn('20240101', opts['daterange'])
        pickle.loads(pickle.dumps(opts))
        with yt_dlp.YoutubeDL(opts) as y:
            self.assertIsInstance(y.params['socket_timeout'], float)

    def test_invalid_types(self):
        for values in ({'ratelimit': 'bad'}, {'retries': -1}, {'retries': 1.5},
                       {'ratelimit': '0'},
                       {'socket_timeout': 0}, {'concurrent_fragment_downloads': 0},
                       {'sleep_interval': float('nan')}):
            with self.subTest(option=next(iter(values))):
                with self.assertRaises(ValueError):
                    build_opts(values)

    def test_preview_preserves_network_options(self):
        from core.info_extractor import extract_info
        for browser in ('chrome', 'edge', 'firefox'):
            self.assertEqual(build_opts({'cookiesfrombrowser': browser})['cookiesfrombrowser'], (browser,))
        options = build_opts({'proxy': 'http://127.0.0.1:1234', 'cookiefile': 'fixture.txt',
                              'http_headers': {'User-Agent': 'audit'}, 'username': 'test',
                              'password': 'TEST_ONLY', 'extractor_args': {'youtube': {'player_client': ['web']}},
                              'socket_timeout': 15, 'retries': 2})
        with patch('core.info_extractor.yt_dlp.YoutubeDL') as factory, patch('core.info_extractor.validate'):
            factory.return_value.__enter__.return_value.extract_info.return_value = {}
            extract_info('https://example.invalid', options)
            effective = factory.call_args.args[0]
            for key in ('proxy', 'cookiefile', 'http_headers', 'username', 'password',
                        'extractor_args', 'socket_timeout', 'retries'):
                self.assertEqual(effective[key], options[key], key)

    def test_cookie_source_and_safe_file_validation(self):
        spec = ('firefox', 'test-profile', None, 'none')
        self.assertEqual(build_opts({'cookiesfrombrowser': spec})['cookiesfrombrowser'], spec)
        with self.assertRaisesRegex(ValueError, 'Choose one Cookie source'):
            build_opts({'cookiefile': 'cookies.txt', 'cookiesfrombrowser': 'chrome'})
        self.assertNotIn('cookiesfrombrowser', build_opts({'cookiefile': 'cookies.txt', 'cookiesfrombrowser': 'None'}))
        self.assertNotIn('SECRET', redact('SID=SECRET; HSID=SECRET; SAPISID=SECRET; __Secure-3PAPISID=SECRET'))
        with tempfile.TemporaryDirectory() as td:
            file = Path(td)/'cookies.txt'
            file.write_text('# Netscape HTTP Cookie File\n.invalid\tTRUE\t/\tFALSE\t0\tSID\tSECRET\n')
            validate_cookie_file(file)
            file.write_text('# Netscape HTTP Cookie File\n.invalid\tTRUE\t/\tFALSE\tbad\tSID\tSECRET\n')
            with self.assertRaisesRegex(ValueError, 'line 2') as failure:
                validate_cookie_file(file)
            self.assertNotIn('SECRET', str(failure.exception))

    def test_postprocessors(self):
        for values in ({'embed_metadata': True, 'embed_chapters': True}, {'remux_video': 'mp4'},
                       {'sponsorblock_mark': 'sponsor'}, {'sponsorblock_remove': 'sponsor'}):
            with yt_dlp.YoutubeDL(build_opts(values)) as y:
                self.assertTrue(y._pps['post_process'])

    def test_credentials(self):
        secret = 'TEST_SECRET_NOT_REAL'
        opts = {'password': secret, 'proxy': f'socks5://user:{secret}@localhost:9999',
                'cookiefile': 'cookies.txt', 'http_headers': {'Authorization': secret, 'User-Agent': 'audit'}}
        self.assertNotIn(secret, json.dumps(persistent_options(opts)))
        self.assertEqual(persistent_options(opts)['cookiefile'], 'cookies.txt')
        self.assertEqual(persistent_url('https://example.invalid/watch?v=id&token='+secret),
                         'https://example.invalid/watch?v=id')
        for text in (opts['proxy'], f'Authorization: Bearer {secret}', f'Cookie: session={secret}',
                     f'https://example.invalid?token={secret}&x=1'):
            self.assertNotIn(secret, redact(text))
        with tempfile.TemporaryDirectory() as td:
            settings = AppSettings(str(Path(td)/'settings.json'))
            settings.update_from(opts); settings.save()
            self.assertNotIn(secret, Path(settings._path).read_text(encoding='utf-8'))
            Path(settings._path).write_text(json.dumps(opts), encoding='utf-8')
            AppSettings(settings._path)
            self.assertNotIn(secret, Path(settings._path).read_text(encoding='utf-8'))
            presets = PresetManager(str(Path(td)/'presets.json'))
            presets.save_user_preset('audit', opts)
            self.assertNotIn(secret, Path(presets._path).read_text(encoding='utf-8'))

    def test_preset_and_gui_option_flow(self):
        with tempfile.TemporaryDirectory() as td, patch('gui.main_window.AppSettings',
                return_value=AppSettings(str(Path(td)/'settings.json'))):
            window = MainWindow()
            panel = window._settings_dialog.settings_panel
            panel.proxy_edit.setText('http://127.0.0.1:12345')
            panel.cookie_file_edit.setText('test-cookie-path.txt')
            panel.cookie_browser_combo.setCurrentIndex(panel.cookie_browser_combo.findData('firefox'))
            panel.path_edit.setText(td)
            panel.outtmpl_edit.setText('%(title)s [%(id)s].%(ext)s')
            panel.ffmpeg_path_edit.setText('C:/ffmpeg/bin')
            panel.cb_subtitles.setChecked(True)
            original = panel.collect_settings_dict()
            panel.apply_preset({'format': 'bv[height<=1080]+ba', 'merge_output_format': 'mkv'})
            current = panel.collect_settings_dict()
            for key in ('proxy','cookiefile','cookiesfrombrowser','download_path','outtmpl','ffmpeg_location','writesubtitles'):
                self.assertEqual(current[key], original[key], key)
            panel.apply_preset(BUILTIN_PRESETS['Audio MP3'])
            self.assertTrue(panel.cb_extract_audio.isChecked())
            panel.apply_preset(BUILTIN_PRESETS['1080p'])
            self.assertFalse(panel.cb_extract_audio.isChecked())
            with self.assertRaisesRegex(ValueError, 'Choose one Cookie source'):
                window._build_ydl_opts()
            panel.cookie_file_edit.clear()
            window._url_input._text_edit.setPlainText('https://www.youtube.com/watch?v=aqz-KE-bpKQ')
            with patch.object(window._manager, 'extract_info') as preview:
                window._on_list_formats()
                effective = preview.call_args.kwargs['ydl_opts']
                self.assertEqual(pickle.dumps(effective), pickle.dumps(window._build_ydl_opts()))
                self.assertEqual(effective['proxy'], current['proxy'])
                self.assertEqual(effective['cookiesfrombrowser'], ('firefox',))
            window.close()

    def test_state_transitions_and_duplicate_run(self):
        changes = []
        task = DownloadTask('https://example.invalid', {},
                            on_status_change=lambda tid, old, new: changes.append(new))
        with patch('core.task.run_ydl', return_value=['verified-file']) as run:
            task.run(); task.run()
            self.assertEqual(run.call_count, 1)
        self.assertEqual(changes, [TaskStatus.PARSING, TaskStatus.READY, TaskStatus.DOWNLOADING,
                                   TaskStatus.POSTPROCESSING, TaskStatus.COMPLETED])
        for error, expected in ((yt_dlp.utils.DownloadError('failure'), TaskStatus.FAILED),
                                (DownloadCancelled(), TaskStatus.CANCELED)):
            task = DownloadTask('https://example.invalid', {})
            with patch('core.task.run_ydl', side_effect=error):
                task.run()
            self.assertEqual(task.status, expected)
        task = DownloadTask('https://example.invalid', {})
        task.cancel(); task.run()
        self.assertEqual(task.status, TaskStatus.CANCELED)

    def test_nonzero_download_is_error(self):
        class FakeYDL:
            def __init__(self, opts): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def add_post_processor(self, *args, **kwargs): pass
            def download(self, urls): return 1
        connection = Connection()
        with patch('core.runtime.yt_dlp.YoutubeDL', FakeYDL):
            _job('https://example.invalid', {}, connection, False)
        self.assertEqual(connection.messages[-1][0], 'error')
        self.assertIn('failure code 1', connection.messages[-1][1]['message'])

    def test_duplicate_queue_and_bad_config(self):
        manager = DownloadManager(max_workers=1)
        with patch.object(manager._executor, 'submit'):
            manager.add_task('https://example.invalid', {})
            with self.assertRaises(ValueError):
                manager.add_task('https://example.invalid', {})
        manager.shutdown()
        with tempfile.TemporaryDirectory() as td:
            file = Path(td)/'settings.json'
            file.write_text('{"max_workers":0,"proxy":5}', encoding='utf-8')
            settings = AppSettings(str(file))
            self.assertEqual(settings.get('max_workers'), 3)
            self.assertEqual(settings.get('proxy'), '')


if __name__ == '__main__':
    unittest.main()
