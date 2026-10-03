import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from app.paths import RuntimePaths
from services.atomic_storage import save_json, load_json
from configs.app_settings import AppSettings
from configs.presets import PresetManager
from services.history_service import HistoryService
from core.runtime_manager import health, tool_path, runtime_options, parse_version, validate_download
from models.errors import FFmpegError, DownloadError


class RuntimePackagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve()
        self.paths=RuntimePaths.resolve(source=self.root)
        self.file=self.root/'settings.json'
    def tearDown(self):self.tmp.cleanup()
    def frozen(self):return RuntimePaths.resolve(frozen=True,executable=self.root/'MediaDownloader.exe',resources=self.root/'_internal',local_appdata=self.root/'user')
    def test_source_paths(self):self.assertEqual(self.paths.config_dir,self.root/'configs')
    def test_frozen_resources(self):self.assertEqual(self.frozen().resources_dir,self.root/'_internal')
    def test_portable_paths(self):
        (self.root/'portable.flag').touch();self.assertEqual(self.frozen().config_dir,self.root/'config')
    def test_installed_paths(self):self.assertEqual(self.frozen().config_dir,self.root/'user/MediaDownloader/config')
    def test_mode_isolation(self):
        installed=self.frozen();(self.root/'portable.flag').touch();self.assertNotEqual(installed.config_dir,self.frozen().config_dir)
    def test_atomic_settings(self):
        s=AppSettings(str(self.file));s.set('retries',4);s.save();self.assertEqual(AppSettings(str(self.file)).get('retries'),4)
    def test_legacy_backup_credentials_removed(self):
        self.file.write_text(json.dumps({'password':'SECRET','proxy':'http://user:SECRET@localhost:8080'}))
        AppSettings(str(self.file))
        self.assertNotIn('SECRET',self.file.read_text(encoding='utf-8'));self.assertNotIn('SECRET',Path(str(self.file)+'.bak').read_text(encoding='utf-8'))
    def test_atomic_history(self):
        h=HistoryService(str(self.file));h.add('id','https://youtu.be/a','中文');self.assertEqual(HistoryService(str(self.file)).list_records()[0]['title'],'中文')
    def test_corrupt_settings_recovery(self):
        s=AppSettings(str(self.file));s.set('retries',3);s.save();s.set('retries',4);s.save();self.file.write_text('{');self.assertEqual(AppSettings(str(self.file)).get('retries'),3)
    def test_corrupt_history_recovery(self):
        h=HistoryService(str(self.file));h.add('one','https://youtu.be/a');h.add('two','https://youtu.be/b');self.file.write_text('{');self.assertEqual(len(HistoryService(str(self.file)).list_records()),1)
    def test_empty_file_defaults(self):self.file.touch();self.assertEqual(load_json(self.file,{'default':True}),{'default':True})
    def test_backup_without_main(self):
        self.file.with_name(self.file.name+'.bak').write_text('{"backup": true}');self.assertEqual(load_json(self.file,{}),{'backup':True})
    def test_temp_ignored(self):
        self.file.with_name(self.file.name+'.123.tmp').write_text('{"partial":true}');self.assertEqual(load_json(self.file,{}),{})
    def test_unicode(self):save_json(self.file,{'中文':'下载路径'});self.assertEqual(load_json(self.file,{}),{'中文':'下载路径'})
    def test_serialization_failure_preserves_old(self):
        save_json(self.file,{'old':True})
        with self.assertRaises(TypeError):save_json(self.file,{'bad':set()})
        self.assertEqual(load_json(self.file,{}),{'old':True})
    def test_fsync_failure_preserves_old(self):
        save_json(self.file,{'old':True})
        with patch('services.atomic_storage.os.fsync',side_effect=OSError('simulated power loss')):
            with self.assertRaises(OSError):save_json(self.file,{'new':True})
        self.assertEqual(load_json(self.file,{}),{'old':True});self.assertEqual(list(self.root.glob('*.tmp')),[])
    def test_replace_failure_preserves_old(self):
        save_json(self.file,{'old':True})
        with patch('services.atomic_storage.os.replace',side_effect=OSError('simulated replacement failure')):
            with self.assertRaises(OSError):save_json(self.file,{'new':True})
        self.assertEqual(load_json(self.file,{}),{'old':True})
    def test_corrupt_main_does_not_overwrite_valid_backup(self):
        save_json(self.file,{'one':1});save_json(self.file,{'two':2});self.file.write_text('bad');save_json(self.file,{'three':3})
        self.assertEqual(load_json(str(self.file)+'.bak',{}),{'one':1})
    def test_atomic_presets(self):
        p=PresetManager(str(self.file));p.save_user_preset('中文',{'format':'b'});self.assertEqual(PresetManager(str(self.file)).get('中文')['format'],'b')
    def test_runtime_health(self):
        with patch('core.runtime_manager.tool_path',return_value='tool'),patch('core.runtime_manager.subprocess.check_output',return_value='tool 8.1.3'),patch('core.runtime_manager.importlib.metadata.version',return_value='2026.8.19'):
            result=health(paths=self.paths);self.assertEqual(result['ffmpeg']['status'],'READY');self.assertEqual(result['config']['status'],'READY')
    def test_missing_ffmpeg(self):
        with patch('core.runtime_manager.tool_path',return_value=None):
            with self.assertRaises(FFmpegError):validate_download({'postprocessors':[{'key':'FFmpegExtractAudio'}]})
    def test_missing_ffprobe(self):
        result=health(paths=self.frozen());self.assertEqual(result['ffprobe']['status'],'NOT_INSTALLED')
    def test_missing_ytdlp(self):
        from importlib.metadata import PackageNotFoundError
        with patch('core.runtime_manager.importlib.metadata.version',side_effect=PackageNotFoundError):self.assertEqual(health(paths=self.frozen())['yt-dlp']['status'],'NOT_INSTALLED')
    def test_missing_js_optional(self):self.assertEqual(runtime_options({},self.frozen())['js_runtimes'],{})
    def test_no_frozen_path_fallback(self):
        with patch('core.runtime_manager.shutil.which',return_value='development-ffmpeg'):self.assertIsNone(tool_path('ffmpeg',paths=self.frozen()))
    def test_version_parsing(self):self.assertEqual(parse_version('deno 2.9.7 (stable)'), '2.9.7')
    def test_ffmpeg_version_parsing(self):self.assertEqual(parse_version('ffmpeg version n8.1.3-14-g330caae0c1-20261001'), 'n8.1.3-14-g330caae0c1-20261001')
    def test_disk_space_known(self):
        s=SimpleNamespace(video=None,audio=None,estimated_size=200)
        with patch('core.runtime_manager.shutil.disk_usage',return_value=SimpleNamespace(free=100)):
            with self.assertRaises(DownloadError):validate_download({'paths':{'home':str(self.root)}},s)
    def test_disk_space_unknown(self):validate_download({},SimpleNamespace(video=None,audio=None,estimated_size=None))
    def test_credential_safe_diagnostics(self):
        text=json.dumps(health(paths=self.frozen()));self.assertNotIn('Authorization',text);self.assertNotIn('cookiefile',text);self.assertNotIn('password',text)

if __name__=='__main__':unittest.main()
