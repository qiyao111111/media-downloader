from core.credentials import redact


class DownloadError(Exception):
    code = 'download'

    def __init__(self, message=''):
        super().__init__(redact(message))


class AuthenticationError(DownloadError):
    code = 'authentication'


class CookieError(AuthenticationError):
    code = 'cookies'


class ProxyError(DownloadError):
    code = 'proxy'


class FFmpegError(DownloadError):
    code = 'ffmpeg'


class FormatError(DownloadError):
    code = 'format'


class CancelledError(DownloadError):
    code = 'cancelled'
