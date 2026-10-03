"""Bundled tool discovery, safe diagnostics and native yt-dlp runtime options."""
import importlib.metadata
import platform
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen
import json
import os
from app.paths import PATHS
from app.version import VERSION
from core.credentials import redact
from models.errors import FFmpegError, DownloadError

NO_WINDOW = subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0


def prepare_environment(options):
    # Only the isolated worker inherits these runtime cache settings.
    if 'deno' in options.get('js_runtimes', {}):
        os.environ['DENO_DIR'] = str(Path(options.get('cachedir') or PATHS.temp_dir/'yt-dlp-cache').parent/'deno')
        os.environ['DENO_NO_UPDATE_CHECK'] = '1'


def tool_path(name, location='', paths=PATHS):
    filename = 'qjs' if name=='quickjs' else name
    if location:
        p = Path(location)
        candidate = p/(filename+'.exe') if p.is_dir() else p.with_name(filename+p.suffix)
    else:
        candidate = paths.runtime_dir/(('runtime/'+filename+'.exe') if name in ('deno','quickjs') else name+'.exe')
    if candidate.is_file():return str(candidate.resolve())
    return shutil.which(name) if not location and paths.mode=='source' and name not in ('deno','quickjs') else None


def runtime_options(inputs, paths=PATHS):
    result = dict(inputs)
    if not result.get('ffmpeg_location'):
        ffmpeg = tool_path('ffmpeg', paths=paths)
        if ffmpeg:result['ffmpeg_location'] = str(Path(ffmpeg).parent)
        elif paths.mode!='source':result['ffmpeg_location'] = str(paths.runtime_dir)
    if 'js_runtimes' not in result:
        quickjs = tool_path('quickjs', paths=paths)
        result['js_runtimes'] = {'quickjs': {'path': quickjs}} if quickjs else {}
    result.setdefault('remote_components', [])
    result.setdefault('cachedir', str(paths.temp_dir/'yt-dlp-cache'))
    return result


def writable(path):
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=path) as stream:stream.write(b'check')
        return True
    except OSError:return False


def parse_version(text):
    found = re.search(r'(?<!\w)n?\d+(?:\.\d+){1,3}(?:[^\s]*)', text)
    return found.group(0) if found else text.splitlines()[0] if text else 'Unknown'


def health(location='', download_dir=None, paths=PATHS):
    result = {'application': {'status':'READY','version':VERSION,'mode':paths.mode,'os':platform.platform(),'architecture':platform.machine()}}
    try:
        result['yt-dlp'] = {'status':'READY','version':importlib.metadata.version('yt-dlp'),'strategy':'bundled Python package'}
    except importlib.metadata.PackageNotFoundError:
        result['yt-dlp'] = {'status':'NOT_INSTALLED','version':'Not Found'}
    for name in ('ffmpeg','ffprobe','quickjs'):
        path = tool_path(name, location if name!='quickjs' else '', paths)
        row = {'path':path or '', 'status':'NOT_INSTALLED','version':'Not Found'}
        if path:
            try:
                text = subprocess.check_output([path,'--version' if name=='quickjs' else '-version'],encoding='utf-8',errors='replace',timeout=10,creationflags=NO_WINDOW,stderr=subprocess.STDOUT)
                row.update(status='READY',version=parse_version(text))
            except (OSError,subprocess.SubprocessError) as exc:row.update(status='ERROR',error=redact(exc))
        if name=='quickjs' and row['status']=='NOT_INSTALLED':row['note']='Some YouTube videos may have limited format availability.'
        result[name] = row
    for name,path in [('config',paths.config_dir),('download',Path(download_dir or paths.download_dir)),('temp',paths.temp_dir)]:
        result[name] = {'status':'READY' if writable(path) else 'ERROR','path':str(path)}
    return result


def check_update():
    # Read-only and explicitly requested. The Python package updates with the application.
    request = Request('https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest',headers={'User-Agent':'MediaDownloader/'+VERSION})
    with urlopen(request,timeout=15) as response:latest=json.load(response)['tag_name']
    return {'installed':importlib.metadata.version('yt-dlp'),'latest':latest,'policy':'Update the application release; no runtime is replaced.'}


def validate_download(options, selection=None):
    needs_merge = selection and selection.video is not None and selection.audio is not None
    needs_ffmpeg = needs_merge or any(p.get('key','').startswith('FFmpeg') for p in options.get('postprocessors',[]))
    if needs_ffmpeg and not tool_path('ffmpeg',options.get('ffmpeg_location','')):
        raise FFmpegError('FFmpeg is required to merge video and audio. Check Runtime Health.')
    if selection and selection.estimated_size:
        folder = Path(options.get('paths',{}).get('home') or PATHS.download_dir)
        if folder.is_dir() and selection.estimated_size > shutil.disk_usage(folder).free:
            raise DownloadError('Not enough disk space for the estimated download size.')
