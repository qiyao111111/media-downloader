"""Checks against the actual native build and final onedir distribution."""
import hashlib
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from app.paths import RuntimePaths
from core.runtime_manager import runtime_options, tool_path, health

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'dist/MediaDownloader'


class DistributionSimplificationTests(unittest.TestCase):
    def test_quickjs_default_and_explicit_override(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'bin/runtime').mkdir(parents=True)
            (root/'bin/runtime/qjs.exe').touch(); (root/'bin/runtime/deno.exe').touch()
            paths = RuntimePaths.resolve(frozen=True, executable=root/'MediaDownloader.exe', resources=root/'_internal', local_appdata=root/'user')
            self.assertEqual(runtime_options({}, paths)['js_runtimes'], {'quickjs': {'path': str((root/'bin/runtime/qjs.exe').resolve())}})
            override = {'deno': {'path': 'explicit-developer-runtime'}}
            self.assertEqual(runtime_options({'js_runtimes': override}, paths)['js_runtimes'], override)
            self.assertEqual(runtime_options({}, paths)['remote_components'], [])

    def test_missing_quickjs_never_uses_system_or_bundled_deno(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'bin/runtime').mkdir(parents=True); (root/'bin/runtime/deno.exe').touch()
            paths = RuntimePaths.resolve(source=root)
            with patch('core.runtime_manager.shutil.which', return_value='system-qjs'):
                self.assertIsNone(tool_path('quickjs', paths=paths))
                self.assertEqual(runtime_options({}, paths)['js_runtimes'], {})

    def test_actual_quickjs_executes_javascript(self):
        result = subprocess.check_output([str(BUNDLE/'bin/runtime/qjs.exe'), '-e', 'console.log(JSON.stringify([1,2,3].map(x=>x*x)))'], encoding='utf-8')
        self.assertEqual(json.loads(result), [1,4,9])

    def test_actual_health_with_utf8_build_configuration(self):
        from core.ffmpeg_utils import version
        with tempfile.TemporaryDirectory() as directory:
            paths=RuntimePaths.resolve(frozen=True,executable=BUNDLE/'MediaDownloader.exe',resources=BUNDLE/'_internal',local_appdata=Path(directory))
            result=health(paths=paths,download_dir=directory)
            for name in ('ffmpeg','ffprobe','quickjs'):
                self.assertEqual(result[name]['status'],'READY',result[name])
            self.assertEqual(result['quickjs']['version'],'0.17.0')
            expected=json.loads((ROOT/'build/runtime-lock.json').read_text())['ffmpeg']['version']
            self.assertIn(expected,version('ffmpeg',str(BUNDLE/'bin')))
            for name in ('ffmpeg','ffprobe'):self.assertEqual(result[name]['version'],expected)

    def test_actual_ffmpeg_license_and_required_capabilities(self):
        exe = str(BUNDLE/'bin/ffmpeg.exe')
        def run(flag): return subprocess.check_output([exe, flag], stderr=subprocess.STDOUT, encoding='utf-8')
        configuration = run('-buildconf'); grant = run('-L')
        for flag in ('--disable-gpl', '--disable-nonfree', '--disable-version3', '--enable-shared'):
            self.assertIn(flag, configuration)
        self.assertNotIn('--enable-gpl', configuration); self.assertIn('version 2.1', grant)
        for codec in ('libdav1d', 'h264', 'vp9', 'aac', 'opus'):
            self.assertIn(codec, run('-decoders'))
        for codec in ('libmp3lame', 'libopus', 'aac', 'flac', 'libopenh264', 'libvpx-vp9', 'libwebp'):
            self.assertIn(codec, run('-encoders'))
        for muxer in ('mp4', 'matroska', 'webm', 'mp3', 'wav', 'flac'):
            self.assertIn(muxer, run('-muxers'))

    def test_native_runtime_and_sources_match_pins(self):
        lock = json.loads((ROOT/'build/runtime-lock.json').read_text())
        receipt=json.loads((BUNDLE/'SOURCES/receipt.json').read_text())
        self.assertEqual(receipt['files'],lock['ffmpeg']['files'])
        self.assertEqual(receipt['ffmpeg_revision'],lock['ffmpeg']['revision'])
        self.assertIn('--disable-gpl',receipt['configure'])
        self.assertIn('--disable-nonfree',receipt['configure'])
        self.assertIn('--extra-version=g330caae0c1-md-b43-r2',receipt['configure'])
        for name, expected in lock['ffmpeg']['files'].items():
            with (BUNDLE/'bin'/name).open('rb') as stream:
                self.assertEqual(hashlib.file_digest(stream, 'sha256').hexdigest(), expected, name)
        with (BUNDLE/'bin/runtime/qjs.exe').open('rb') as stream:
            self.assertEqual(hashlib.file_digest(stream,'sha256').hexdigest(),lock['quickjs']['sha256'])
        source_lock = json.loads((ROOT/'build/native-runtime-lock.json').read_text())
        for item in source_lock['sources']:
            with (BUNDLE/'SOURCES'/item['archive']).open('rb') as stream:
                self.assertEqual(hashlib.file_digest(stream,'sha256').hexdigest(), item['sha256'], item['component'])
        with zipfile.ZipFile(BUNDLE/'SOURCES/native-relink-materials.zip') as archive:
            names = archive.namelist()
            self.assertTrue(any(n.startswith('ffmpeg-objects/') for n in names))
            for library in ('libmp3lame.a', 'libdav1d.a', 'libopenh264.a', 'libvpx.a', 'libwebp.a'):
                self.assertIn('static-libraries/'+library, names)
            self.assertIn('toolchain-runtime/libwinpthread.a', names)

    def test_actual_ytdlp_metadata_with_chapters(self):
        import wave
        import yt_dlp
        from yt_dlp.postprocessor.ffmpeg import FFmpegMetadataPP
        with tempfile.TemporaryDirectory(prefix='章节 metadata ') as directory:
            folder=Path(directory); source=folder/'input.wav'; output=folder/'output.mkv'
            with wave.open(str(source),'wb') as audio:
                audio.setparams((1,2,8000,0,'NONE','not compressed'))
                audio.writeframes(b'\0\0'*8000)
            subprocess.run([str(BUNDLE/'bin/ffmpeg.exe'),'-v','error','-i',str(source),
                            '-c','copy',str(output)],check=True,capture_output=True)
            info={'filepath':str(output),'ext':'mkv','title':'章节测试', 'duration':1,
                  'chapters':[{'start_time':0,'end_time':.5,'title':'开始'},
                              {'start_time':.5,'end_time':1,'title':'结束'}]}
            with yt_dlp.YoutubeDL({'ffmpeg_location':str(BUNDLE/'bin'),'quiet':True}) as ydl:
                FFmpegMetadataPP(ydl,add_metadata=True,add_chapters=True).run(info)
            result=json.loads(subprocess.check_output([str(BUNDLE/'bin/ffprobe.exe'),'-v','error',
                '-show_chapters','-show_streams','-show_format','-of','json',str(output)],encoding='utf-8'))
            self.assertEqual(result['format']['tags']['title'],'章节测试')
            self.assertEqual([c['tags']['title'] for c in result['chapters']],['开始','结束'])
            self.assertEqual(result['streams'][0]['codec_name'],'pcm_s16le')
            self.assertFalse(output.with_suffix('.meta').exists())

    def test_existing_explicit_video_and_webp_encoders_work(self):
        import struct, zlib
        def chunk(kind, data):
            return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
        png = b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',16,16,8,2,0,0,0))
        png += chunk(b'IDAT',zlib.compress((b'\0'+b'\x80\x40\x20'*16)*16))+chunk(b'IEND',b'')
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory); image=folder/'input.png'; image.write_bytes(png)
            for codec,extension in [('libopenh264','mp4'),('libvpx-vp9','webm'),('libwebp','webp')]:
                output=folder/('output.'+extension)
                result=subprocess.run([str(BUNDLE/'bin/ffmpeg.exe'),'-v','error','-i',str(image),'-frames:v','1','-pix_fmt','yuv420p','-c:v',codec,str(output)],capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace'))
                self.assertGreater(output.stat().st_size,0)
            import yt_dlp
            from yt_dlp.postprocessor.ffmpeg import FFmpegThumbnailsConvertorPP
            with yt_dlp.YoutubeDL({'ffmpeg_location':str(BUNDLE/'bin'),'quiet':True}) as ydl:
                converter=FFmpegThumbnailsConvertorPP(ydl)
                jpeg=converter.convert_thumbnail(str(image),'jpg')
                webp=converter.convert_thumbnail(jpeg,'webp')
                restored=converter.convert_thumbnail(webp,'png')
                self.assertGreater(Path(restored).stat().st_size,0)

    def test_removed_binaries_notices_and_replaceable_qt(self):
        self.assertFalse(list(BUNDLE.rglob('deno.exe')))
        self.assertFalse(list(BUNDLE.rglob('ffplay.exe')))
        self.assertFalse(list(BUNDLE.rglob('opengl32sw.dll')))
        self.assertFalse(list((BUNDLE/'licenses').rglob('*Deno*')))
        for name in ('Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll'):
            self.assertTrue((BUNDLE/'_internal/PySide6'/name).is_file(), name)
        self.assertTrue((BUNDLE/'_internal/PySide6/plugins/platforms/qwindows.dll').is_file())
        for name in ('quickjs-LICENSE.txt','lame-COPYING.txt','LLVM-runtime-LICENSE.txt','MinGW-w64-runtime-NOTICES.txt','Winpthreads-LICENSE.txt','ffmpeg-SOURCE-NOTICES.txt'):
            self.assertTrue((BUNDLE/'licenses'/name).is_file(), name)
        for component in ('libcxx','libcxxabi','libunwind','compiler-rt'):
            self.assertTrue((BUNDLE/'licenses'/('LLVM-'+component+'-LICENSE.txt')).is_file())

    def test_actual_portable_contains_sources_and_notices(self):
        with zipfile.ZipFile(ROOT/'dist/release/MediaDownloader-Portable.zip') as archive:
            for relative in ('THIRD_PARTY_NOTICES.txt','licenses/quickjs-LICENSE.txt','SOURCES/BUILD_INSTRUCTIONS.txt','SOURCES/native-relink-materials.zip','source-offer/README.txt'):
                self.assertEqual(archive.read('MediaDownloader-Portable/'+relative), (BUNDLE/relative).read_bytes())

    def test_sandbox_maps_only_test_kit(self):
        import xml.etree.ElementTree as ET
        folders = ET.parse(ROOT/'release-test/MediaDownloader-Test.wsb').findall('.//MappedFolder')
        self.assertEqual(len(folders), 1)
        self.assertEqual(Path(folders[0].findtext('HostFolder')).resolve(), (ROOT/'release-test').resolve())
        self.assertEqual(folders[0].findtext('ReadOnly'), 'true')


if __name__ == '__main__': unittest.main()
