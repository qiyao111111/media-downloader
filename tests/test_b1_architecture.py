import json
import logging
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from models.download import DownloadRecord, TaskStatus
from models.format import FormatProfile
from models.errors import CookieError
from core.task import DownloadTask
from core.manager import DownloadManager
from core.cookies_manager import cookie_options, validate, safe_display
from core.proxy_manager import proxy_options, safe_display as proxy_display
from core.option_builder import build_opts
from services.settings_service import SettingsService, merge_preset
from services.history_service import HistoryService
from services.logging_service import configure_logging


class ArchitectureChecks(unittest.TestCase):
    def test_state_model_terminal_guards(self):
        record = DownloadRecord('id', 'url')
        for status in (TaskStatus.PARSING, TaskStatus.READY, TaskStatus.DOWNLOADING,
                       TaskStatus.POSTPROCESSING, TaskStatus.COMPLETED):
            record.transition(status)
        self.assertTrue(record.started_at and record.completed_at)
        for state in TaskStatus:
            if state != TaskStatus.COMPLETED:
                with self.assertRaises(ValueError):
                    record.transition(state)
        for terminal in (TaskStatus.FAILED, TaskStatus.CANCELLED):
            r = DownloadRecord('id', 'url'); r.transition(terminal)
            with self.assertRaises(ValueError): r.transition(TaskStatus.COMPLETED)
        self.assertEqual(len(TaskStatus), 8)
        self.assertEqual(FormatProfile(width=15360, height=8640).height, 8640)

    def test_settings_preset_separation(self):
        with tempfile.TemporaryDirectory() as td:
            service = SettingsService(str(Path(td)/'settings.json'))
            service.update_from({'download_path': td, 'proxy': 'socks5://user:SECRET@localhost:1080',
                                 'concurrent_fragment_downloads': 4, 'max_workers': 2})
            model = service.model()
            self.assertEqual((model.max_concurrent_downloads, model.concurrent_fragments), (2, 4))
            merged = merge_preset(service.to_dict(), {'proxy': 'different', 'download_path': 'bad',
                                  'ffmpeg_location': 'bad', 'format': 'bv[height<=1080]+ba'})
            self.assertEqual(merged['download_path'], td)
            self.assertIn('SECRET', merged['proxy'])
            options = build_opts(merged)
            self.assertEqual(options['paths']['home'], td)
            self.assertNotIn('max_workers', options)
            service.save()
            self.assertNotIn('SECRET', Path(service._path).read_text())

    def test_cookie_proxy_boundaries(self):
        spec = ('firefox', 'profile', None, 'none')
        self.assertEqual(cookie_options(spec)['cookiesfrombrowser'], spec)
        self.assertEqual(safe_display(cookie_options(spec))['profile'], 'profile')
        with self.assertRaises(ValueError): cookie_options(spec, 'cookies.txt')
        with self.assertRaises(CookieError): validate({'cookiefile': 'B1-nonexistent-file.txt'})
        for protocol in ('http', 'socks5', 'socks5h'):
            endpoint = protocol+'://user:SECRET@127.0.0.1:1234'
            self.assertEqual(proxy_options(endpoint)['proxy'], endpoint)
            self.assertNotIn('SECRET', proxy_display(endpoint))
        for invalid in ('bad', 'http://host:99999', 'http://host:0'):
            with self.assertRaises(ValueError): proxy_options(invalid)

    def test_history_serialization_and_legacy(self):
        with tempfile.TemporaryDirectory() as td:
            file = Path(td)/'history.json'
            file.write_text(json.dumps([{'task_id':'old','url':'https://test.invalid/?token=SECRET',
                                        'status':'canceled','Cookie':'SECRET'}]))
            service = HistoryService(str(file))
            self.assertEqual(service.list_records()[0]['status'], 'cancelled')
            service.add_record({'task_id':'new','url':'https://test.invalid','title':'test','status':'queued',
                                'password':'SECRET'})
            service.update_record('new', status='completed', quality='4320P', output_path='output.mp4',
                                  error='Authorization: SECRET')
            self.assertNotIn('SECRET', file.read_text())
            result=service.list_records();result[0]['status']='bad'
            self.assertEqual(service.list_records()[0]['status'], 'cancelled')
            self.assertEqual(HistoryService(str(file)).list_records()[1]['output_path'], 'output.mp4')
            service.clear_history(); self.assertEqual(service.list_records(), [])

    def test_manager_events_retry_and_queue(self):
        events=[]
        manager=DownloadManager(1, on_event=lambda event, data:events.append(event))
        with patch.object(manager._executor, 'submit'):
            tid=manager.add_task('url', {})
            with self.assertRaises(ValueError): manager.add_task('url', {})
            with self.assertRaises(ValueError): manager.retry_task(tid)
            with self.assertRaises(ValueError): manager.configure_workers(2)
            task=manager.get_task(tid)
            with patch('core.task.run_ydl', return_value=['output.mp4']): task.run()
            new=manager.retry_task(tid)
            self.assertNotEqual(new, tid)
            self.assertIn('task_completed', events)
            self.assertTrue(manager.remove_task(tid))
            self.assertNotIn(tid, [t.id for t in manager.get_all_tasks()])
            manager.get_task(new).record.transition(TaskStatus.CANCELLED)
        manager.configure_workers(2)
        self.assertEqual(manager._max_workers, 2)
        manager.shutdown()

    def test_rotating_logs_are_masked(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'desktop.log';logger=configure_logging(path)
            for level in (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR):
                logger.log(level, 'socks5://user:SECRET@host:1080 Authorization: SECRET')
            for handler in list(logger.handlers):
                handler.flush(); logger.removeHandler(handler);handler.close()
            self.assertNotIn('SECRET', path.read_text())
            self.assertIn('DEBUG', path.read_text())
