"""Build the pinned Windows native runtime from verified, unpacked sources.

Build tools are development-only. Each invocation/working directory is recorded;
the source archives, commands and generated configuration accompany releases.
"""
import hashlib
import ctypes
import json
import os
import shlex
import shutil
import subprocess
import tarfile
import zipfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / '.tools/b43'
TOOLS = CACHE / 'toolchains'
LLVM = TOOLS / 'llvm-mingw-20260922-ucrt-x86_64/bin'
MSYS = TOOLS / 'msys64/usr/bin'
BUILD = CACHE / 'native-build'
PREFIX = BUILD / 'prefix'
SOURCES = CACHE / 'native-sources'
COMMANDS = []


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(args, cwd=ROOT, env=None):
    args = list(map(str, args))
    COMMANDS.append({'cwd': str(cwd), 'argv': args})
    (BUILD / 'commands.json').write_text(json.dumps(COMMANDS, indent=2), encoding='utf-8')
    print(shlex.join(args), flush=True)
    subprocess.run(args, cwd=cwd, env=env or ENV, check=True)


def unix(path):
    return subprocess.check_output([str(MSYS / 'cygpath.exe'), '-u', str(path)], text=True, encoding='utf-8').strip()


def source(component):
    directory = CACHE / 'quickjs/source' if component == 'quickjs' else SOURCES / component
    return next(directory.iterdir())


def prepare_sources():
    lock = json.loads((ROOT / 'build/native-runtime-lock.json').read_text(encoding='utf-8'))
    SOURCES.mkdir(parents=True, exist_ok=True)
    for item in lock['sources']:
        target = SOURCES / item['archive']
        existing = CACHE / 'quickjs/source.tar.gz' if item['component'] == 'quickjs' else ROOT / '.tools/license-sources' / item['archive']
        if not target.is_file() or digest(target) != item['sha256']:
            original = existing if existing.is_file() and digest(existing) == item['sha256'] else fetch_archive(item)
            shutil.copy2(original, target)
        destination = CACHE / 'quickjs/source' if item['component'] == 'quickjs' else SOURCES / item['component']
        if not destination.exists():
            destination.mkdir(parents=True)
            with tarfile.open(target) as archive:
                archive.extractall(destination, filter='data')
    for item in lock['toolchains']:
        archive = TOOLS / item['archive']
        if not archive.is_file() or digest(archive) != item['sha256']:
            TOOLS.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fetch_archive(item), archive)
        target = TOOLS / ('llvm-mingw-20260922-ucrt-x86_64' if item['archive'].endswith('.zip') else 'msys64')
        if not target.exists():
            if archive.suffix == '.zip':
                with zipfile.ZipFile(archive) as files:files.extractall(TOOLS)
            else:
                with tarfile.open(archive) as files:files.extractall(TOOLS, filter='data')
    for tool in ('make.exe', 'nasm.exe', 'pkgconf.exe', 'diff.exe', 'perl.exe'):
        if not (MSYS / tool).is_file():
            raise SystemExit('Install make, nasm, pkgconf, diffutils and perl in the isolated MSYS2 root; see docs/B4_3_FFMPEG_BUILD.md')
    return lock


def fetch_archive(item):
    target = CACHE / 'downloads' / item['archive']
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and digest(target) == item['sha256']:return target
    temporary = target.with_suffix(target.suffix + '.tmp')
    try:
        request = urllib.request.Request(item['url'], headers={'User-Agent': 'MediaDownloader-runtime-build'})
        with urllib.request.urlopen(request, timeout=60) as response, temporary.open('wb') as stream:
            shutil.copyfileobj(response, stream)
        if digest(temporary) != item['sha256']:raise ValueError('Source/toolchain checksum mismatch: ' + item['archive'])
        temporary.replace(target)
    finally:temporary.unlink(missing_ok=True)
    return target


def cmake(component, options):
    directory = BUILD / component
    run([ROOT / '.venv/Scripts/cmake.exe', '-S', source(component), '-B', directory,
         '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_SYSTEM_NAME=Windows',
         '-DCMAKE_C_COMPILER=' + str(LLVM / 'x86_64-w64-mingw32-clang.exe'),
         '-DCMAKE_INSTALL_PREFIX=' + str(PREFIX), *options])
    return directory


ENV = dict(os.environ)
ENV['PATH'] = os.pathsep.join(map(str, [LLVM, MSYS, ROOT / '.venv/Scripts'])) + os.pathsep + ENV['PATH']
ENV['PKG_CONFIG_LIBDIR'] = str(PREFIX / 'lib/pkgconfig')
ENV['GIT_CEILING_DIRECTORIES'] = str(SOURCES)
ENV.pop('PKG_CONFIG_PATH', None)


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    PREFIX.mkdir(exist_ok=True)
    lock = prepare_sources()
    for item in lock['sources']:
        assert digest(SOURCES / item['archive']) == item['sha256'], item['component']
    cm = ROOT / '.venv/Scripts/cmake.exe'
    qjs = CACHE / 'quickjs/build'
    run([cm, '-S', source('quickjs'), '-B', qjs, '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release',
         '-DCMAKE_C_COMPILER=' + str(LLVM / 'x86_64-w64-mingw32-clang.exe'),
         '-DCMAKE_CXX_COMPILER=' + str(LLVM / 'x86_64-w64-mingw32-clang++.exe'),
         '-DQJS_BUILD_CLI_STATIC=ON', '-DQJS_BUILD_CLI_WITH_STATIC_MIMALLOC=OFF',
         '-DQJS_BUILD_TESTS=OFF', '-DQJS_BUILD_EXAMPLES=OFF'])
    run([cm, '--build', qjs, '--target', 'qjs_exe', '-j', '8'])
    zlib = cmake('zlib', ['-DCMAKE_POLICY_VERSION_MINIMUM=3.5'])
    run([cm, '--build', zlib, '--target', 'zlibstatic', '-j', '8'])
    for directory in ('lib/pkgconfig', 'include'):
        (PREFIX / directory).mkdir(parents=True, exist_ok=True)
    shutil.copy2(next(zlib.glob('*z*.a')), PREFIX / 'lib/libz.a')
    shutil.copy2(source('zlib') / 'zlib.h', PREFIX / 'include/zlib.h')
    shutil.copy2(zlib / 'zconf.h', PREFIX / 'include/zconf.h')
    (PREFIX / 'lib/pkgconfig/zlib.pc').write_text(f'prefix={unix(PREFIX)}\nlibdir=${{prefix}}/lib\nincludedir=${{prefix}}/include\nName: zlib\nDescription: zlib\nVersion: 1.3.1\nLibs: -L${{libdir}} -lz\nCflags: -I${{includedir}}\n')

    opus = cmake('opus', ['-DOPUS_BUILD_SHARED_LIBRARY=OFF', '-DBUILD_SHARED_LIBS=OFF',
                         '-DBUILD_TESTING=OFF', '-DOPUS_BUILD_TESTING=OFF', '-DOPUS_BUILD_PROGRAMS=OFF',
                         '-DOPUS_INSTALL_PKG_CONFIG_MODULE=ON', '-DOPUS_DRED=OFF', '-DOPUS_OSCE=OFF',
                         '-DOPUS_PACKAGE_VERSION=1.6.1'])
    run([cm, '--build', opus, '-j', '8'])
    run([cm, '--install', opus])

    native = BUILD / 'meson.ini'
    native.write_text("[binaries]\n" + '\n'.join(
        name + ' = ' + repr(str(path).replace('\\', '/')) for name, path in (
            ('c', LLVM / 'x86_64-w64-mingw32-clang.exe'), ('ar', LLVM / 'llvm-ar.exe'),
            ('strip', LLVM / 'llvm-strip.exe'), ('nasm', MSYS / 'nasm.exe'), ('pkg-config', MSYS / 'pkgconf.exe'))), encoding='utf-8')
    dav1d = BUILD / 'dav1d'
    meson = ROOT / '.venv/Scripts/meson.exe'
    setup = 'setup' if not (dav1d / 'meson-private/coredata.dat').exists() else 'configure'
    if setup == 'setup':
        run([meson, 'setup', dav1d, source('dav1d'), '--native-file', native,
             '--prefix', PREFIX, '--libdir', 'lib', '--default-library=static', '--buildtype=release',
             '--wrap-mode=nodownload', '-Denable_tools=false', '-Denable_tests=false', '-Denable_examples=false', '-Denable_docs=false'])
    run([meson, 'compile', '-C', dav1d, '-j', '8'])
    run([meson, 'install', '-C', dav1d])

    shell_env = dict(ENV)
    shell_env['CC'] = unix(LLVM / 'x86_64-w64-mingw32-clang.exe')
    shell_env['AR'] = unix(LLVM / 'llvm-ar.exe')
    shell_env['RANLIB'] = unix(LLVM / 'llvm-ranlib.exe')
    shell_env['CFLAGS'] = '-O2 -Wno-error=implicit-function-declaration'
    lame = BUILD / 'lame'
    lame.mkdir(exist_ok=True)
    run([MSYS / 'bash.exe', '-c', shlex.join([unix(source('lame') / 'configure'),
         '--host=x86_64-w64-mingw32', '--prefix=' + unix(PREFIX), '--disable-shared',
         '--enable-static', '--disable-frontend', '--disable-decoder', '--disable-nasm'])], lame, shell_env)
    run([MSYS / 'make.exe', '-j8'], lame, shell_env)
    run([MSYS / 'make.exe', 'install'], lame, shell_env)

    webp = cmake('webp', ['-DBUILD_SHARED_LIBS=OFF', '-DWEBP_LINK_STATIC=ON', '-DWEBP_USE_THREAD=OFF',
                         *['-DWEBP_BUILD_' + name + '=OFF' for name in
                           ('ANIM_UTILS','CWEBP','DWEBP','GIF2WEBP','IMG2WEBP','VWEBP','WEBPINFO','WEBPMUX','LIBWEBPMUX','EXTRAS','FUZZTEST')]])
    run([cm, '--build', webp, '-j', '8'])
    run([cm, '--install', webp])

    shell_env['CXX'] = unix(LLVM / 'x86_64-w64-mingw32-clang++.exe')
    vpx = BUILD / 'vpx';vpx.mkdir(exist_ok=True)
    run([MSYS / 'bash.exe', '-c', shlex.join([unix(source('vpx') / 'configure'),
         '--prefix=' + unix(PREFIX), '--target=x86_64-win64-gcc', '--as=nasm', '--enable-static',
         '--disable-shared', '--disable-examples', '--disable-tools', '--disable-docs', '--disable-unit-tests',
         '--disable-vp8', '--enable-vp9', '--enable-vp9-highbitdepth', '--disable-vp9-decoder', '--disable-avx512'])], vpx, shell_env)
    run([MSYS / 'make.exe', '-j8'], vpx, shell_env)
    run([MSYS / 'make.exe', 'install'], vpx, shell_env)

    h264 = BUILD / 'openh264';h264.mkdir(exist_ok=True)
    h264_args = ['-f', unix(source('openh264') / 'Makefile'), 'OS=mingw_nt', 'ARCH=x86_64',
                 'CC=' + shell_env['CC'], 'CXX=' + shell_env['CXX'], 'AR=' + shell_env['AR'],
                 'USE_ASM=No', 'PREFIX=' + unix(PREFIX),
                 'STATIC_LDFLAGS=-Wl,-Bstatic -lc++ -lc++abi -lunwind -Wl,-Bdynamic', 'V=No']
    run([MSYS / 'make.exe', *h264_args, '-j8', 'libopenh264.a'], h264, shell_env)
    run([MSYS / 'make.exe', *h264_args, 'install-static'], h264, shell_env)

    # MSYS pkgconf escapes UTF-8 Windows paths in a form configure cannot use.
    # Keep build-only .pc prefixes ASCII; distributed paths are unaffected.
    short = ctypes.create_unicode_buffer(32768)
    if not ctypes.windll.kernel32.GetShortPathNameW(str(PREFIX), short, len(short)):
        raise OSError('Cannot resolve native build prefix')
    if not short.value.isascii():
        raise ValueError('Native compilation requires an ASCII checkout or enabled Windows short filenames')
    for pc in (PREFIX / 'lib/pkgconfig').glob('*.pc'):
        content = pc.read_text(encoding='utf-8').replace(str(PREFIX).replace('\\', '/'), unix(short.value)).replace(unix(PREFIX), unix(short.value))
        content = content.replace('-lpthread', '-Wl,-Bstatic -lpthread -Wl,-Bdynamic')
        lines = content.splitlines()
        lines = ['prefix=' + unix(short.value) if line.startswith('prefix=') else line for line in lines]
        pc.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    ffmpeg = BUILD / 'ffmpeg'
    ffmpeg.mkdir(exist_ok=True)
    flags = ['--prefix=' + unix(PREFIX), '--target-os=mingw32', '--arch=x86_64',
             '--cc=' + unix(LLVM / 'x86_64-w64-mingw32-clang.exe'), '--ld=' + unix(LLVM / 'x86_64-w64-mingw32-clang.exe'),
             '--ar=' + unix(LLVM / 'llvm-ar.exe'), '--ranlib=' + unix(LLVM / 'llvm-ranlib.exe'),
             '--nm=' + unix(LLVM / 'llvm-nm.exe'), '--strip=' + unix(LLVM / 'llvm-strip.exe'),
             '--pkg-config=' + unix(MSYS / 'pkgconf.exe'), '--pkg-config-flags=--static',
             '--extra-cflags=-I' + unix(short.value) + '/include', '--extra-ldflags=-L' + unix(short.value) + '/lib',
             '--extra-version=g330caae0c1-md-b43-r2', '--disable-everything', '--disable-autodetect',
             '--disable-gpl', '--disable-nonfree', '--disable-version3', '--disable-avdevice',
             '--disable-doc', '--disable-debug', '--disable-ffplay', '--disable-network',
             '--enable-shared', '--disable-static', '--enable-w32threads', '--disable-pthreads',
             '--enable-ffmpeg', '--enable-ffprobe', '--enable-libdav1d', '--enable-libopus',
             '--enable-libmp3lame', '--enable-zlib',
             '--enable-libwebp', '--enable-libvpx', '--enable-libopenh264',
             '--enable-decoder=h264,vp9,libdav1d,opus,aac,mp3,flac,vorbis,mpeg4,pcm_s16le,pcm_s16be,pcm_f32le,pcm_f64le,alac,mjpeg,png,webp,subrip,webvtt,ass,mov_text',
             '--enable-encoder=libmp3lame,libopus,aac,flac,pcm_s16le,wrapped_avframe,mjpeg,png,mov_text,subrip,webvtt,ass,libwebp,libvpx_vp9,libopenh264,flv',
             '--enable-demuxer=mov,matroska,ogg,mp3,aac,flac,wav,mjpeg,image2,image2pipe,srt,webvtt,ass,concat,avi,flv,lrc,ffmetadata',
             '--enable-muxer=mp4,mov,ipod,matroska,webm,webp,ogg,mp3,adts,flac,wav,null,image2,image2pipe,srt,webvtt,ass,avi,flv,lrc',
             '--enable-parser=aac,h264,vp9,av1,mpegaudio,flac,opus,mpeg4video,vorbis',
             '--enable-bsf=aac_adtstoasc,extract_extradata,h264_mp4toannexb,av1_frame_merge,av1_frame_split,vp9_superframe,vp9_superframe_split,vp9_metadata,dump_extra,mjpeg2jpeg',
             '--enable-filter=aformat,aresample,anull,null,format,scale', '--enable-protocol=file,pipe,concat']
    shell_env['PKG_CONFIG_LIBDIR'] = unix(PREFIX / 'lib/pkgconfig')
    run([MSYS / 'bash.exe', '-c', shlex.join([unix(source('ffmpeg') / 'configure'), *flags])], ffmpeg, shell_env)
    run([MSYS / 'make.exe', '-j8'], ffmpeg, shell_env)
    run([MSYS / 'make.exe', 'install'], ffmpeg, shell_env)
    write_receipt(lock, flags)


def write_receipt(lock, flags):
    qjs = CACHE / 'quickjs/build'
    receipt = {'sources': lock['sources'], 'toolchains': lock['toolchains'], 'ffmpeg_revision': '330caae0c1acccd2222edc52a05940c574561ce5',
               'configure': flags, 'source_modifications': 'None',
               'quickjs_sha256': digest(qjs / 'qjs.exe'),
               'files': {p.name: digest(p) for p in sorted((PREFIX / 'bin').iterdir()) if p.suffix.lower() in ('.exe', '.dll')}}
    (BUILD / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
