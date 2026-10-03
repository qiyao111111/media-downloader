"""A terminable boundary around yt-dlp; download logic stays in yt-dlp."""

import multiprocessing
import os
import signal
import subprocess
from pathlib import Path

import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor
from yt_dlp.postprocessor.ffmpeg import FFmpegPostProcessor

from core.credentials import SafeLogger
from core.cookies_manager import validate
from models.errors import DownloadError, CancelledError, FFmpegError, CookieError, ProxyError, FormatError, AuthenticationError

def map_error(exc):
    if isinstance(exc, DownloadError):
        return exc
    # Cookie-loading exceptions retain their chain, rather than matching UI stderr.
    from yt_dlp.cookies import CookieLoadError
    from yt_dlp.networking.exceptions import ProxyError as NativeProxyError
    current = exc
    seen = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, CookieLoadError):
            return CookieError(exc)
        if isinstance(current, NativeProxyError):
            return ProxyError(exc)
        current = current.__cause__ or current.__context__
    return DownloadError(exc)


DownloadCancelled = CancelledError


def _job(url, options, connection, preview):
    from core.runtime_manager import prepare_environment
    prepare_environment(options)
    if os.name != 'nt':
        os.setsid()
    options = dict(options)
    options['logger'] = SafeLogger()
    outputs = []

    def report(kind, data):
        # Keep credential-bearing media URLs out of callbacks and UI logs.
        data = dict(data)
        info = data.get('info_dict', {})
        data['info_dict'] = {k: info[k] for k in ('title', 'id', 'format_id', 'width', 'height',
                            'fps', 'dynamic_range', 'vcodec', 'acodec', 'filepath', 'ext', 'thumbnail') if k in info}
        connection.send((kind, data))

    class VerifyOutputPP(PostProcessor):
        def run(self, info):
            path = Path(info['filepath'])
            if not path.is_file() or path.stat().st_size == 0:
                raise yt_dlp.utils.PostProcessingError('Final output is missing or empty')
            outputs.append(str(path))
            return [], info

    class ReadyPP(PostProcessor):
        def run(self, info):
            if info.get('requested_formats') and not FFmpegPostProcessor(self._downloader).available:
                raise FFmpegError('FFmpeg is required for separate video/audio streams')
            report('progress', {'status': 'ready', 'info_dict': info})
            return [], info

    try:
        if preview:
            from core.info_extractor import extract_info
            result = extract_info(url, options)
        else:
            validate(options)
            options['progress_hooks'] = [lambda data: report('progress', data)]
            options['postprocessor_hooks'] = [lambda data: report('postprocess', data)]
            with yt_dlp.YoutubeDL(options) as ydl:
                if '+' in str(options.get('format', '')) and not FFmpegPostProcessor(ydl).available:
                    raise FFmpegError('FFmpeg is required for separate video/audio streams')
                ydl.add_post_processor(ReadyPP(ydl), when='before_dl')
                ydl.add_post_processor(VerifyOutputPP(ydl), when='after_move')
                code = ydl.download([url])
                if code:
                    raise yt_dlp.utils.DownloadError(f'yt-dlp returned failure code {code}')
                if not outputs and not options.get('skip_download') and not options.get('simulate'):
                    raise yt_dlp.utils.DownloadError('No final media output was produced')
            result = outputs
        connection.send(('result', result))
    except Exception as exc:
        error = map_error(exc)
        if isinstance(error, CookieError) and options.get('cookiesfrombrowser'):
            error = CookieError('无法直接读取浏览器 Cookies。请导出 cookies.txt 后重试。 ' + str(error))
        connection.send(('error', {'code': error.code, 'message': str(error)}))
    finally:
        connection.close()


def _stop(process):
    if process.pid is None:
        return
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.join(timeout=5)
    if process.is_alive():
        process.kill()
        process.join(timeout=5)
    if process.is_alive():
        raise RuntimeError('Download worker did not stop')


def run_ydl(url, options, cancel_event, on_progress=None, on_postprocess=None, *, preview=False):
    if cancel_event.is_set():
        raise DownloadCancelled()
    opts = dict(options)
    progress_hooks = opts.pop('progress_hooks', [])
    pp_hooks = opts.pop('postprocessor_hooks', [])
    ctx = multiprocessing.get_context('spawn')
    receiver, sender = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_job, args=(url, opts, sender, preview))
    result = None
    received_result = False
    try:
        process.start()
        sender.close()
        while True:
            if cancel_event.is_set():
                _stop(process)
                raise DownloadCancelled()
            try:
                available = receiver.poll(.05)
            except (EOFError, OSError):
                break
            if available:
                try:
                    kind, data = receiver.recv()
                except (EOFError, OSError):
                    break
                if kind == 'error':
                    error_type = {'cookies': CookieError, 'proxy': ProxyError, 'ffmpeg': FFmpegError,
                                  'format': FormatError, 'authentication': AuthenticationError}.get(data['code'], DownloadError)
                    raise error_type(data['message'])
                if kind == 'result':
                    result, received_result = data, True
                elif kind in ('progress', 'postprocess'):
                    callback = on_progress if kind == 'progress' else on_postprocess
                    if callback:
                        callback(data)
                    for hook in progress_hooks if kind == 'progress' else pp_hooks:
                        hook(data)
            elif not process.is_alive():
                break
        process.join(timeout=5)
        if cancel_event.is_set():
            raise DownloadCancelled()
        if not received_result or process.exitcode != 0:
            raise DownloadError('Download worker exited without a successful result')
        return result
    finally:
        if process.is_alive():
            _stop(process)
        receiver.close()
        sender.close()
