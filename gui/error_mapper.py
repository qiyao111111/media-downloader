"""Friendly UI messages only; core errors and retry policy remain unchanged."""
from core.credentials import redact
from models.errors import CookieError,AuthenticationError,ProxyError,FFmpegError,FormatError,CancelledError
from PySide6.QtWidgets import QMessageBox
from i18n import tr,bind


def error_key(error):
    text=redact(error).lower()
    if text==tr('path_missing').lower():return 'path_missing'
    if isinstance(error,CancelledError):return 'error.cancelled'
    if isinstance(error,CookieError):
        return 'error.cookies' if any(word in text for word in ('chrome','edge','browser','dpapi','decrypt','database')) else 'error.cookie_file'
    if isinstance(error,ProxyError):return 'error.proxy'
    if isinstance(error,FFmpegError):return 'error.ffmpeg_missing' if any(word in text for word in ('missing','not found','required','unavailable')) else 'error.merge'
    if any(word in text for word in ('disk space','disk full','no space','not enough space','errno 28','winerror 112')):return 'error.disk'
    if '403' in text:return 'error.403'
    if 'challenge' in text or 'confirm you' in text or 'not a bot' in text:return 'error.challenge'
    if isinstance(error,AuthenticationError) or any(word in text for word in ('login required','sign in','authentication required')):return 'error.auth'
    if isinstance(error,FormatError):return 'error.format'
    if any(word in text for word in ('invalid url','unsupported url','not a valid url')):return 'error.invalid_url'
    if any(word in text for word in ('video unavailable','private video','removed video','not available','restricted')):return 'error.unavailable'
    if any(word in text for word in ('timed out','connection','network','unable to download','name resolution')):return 'error.network'
    return 'error.generic'


def error_text(error):
    return tr(error_key(error)),redact(error)


def show_error(parent,error,title=None):
    message,details=error_text(error)
    box=QMessageBox(QMessageBox.Warning,tr(title or 'error.title'),message,parent=parent)
    bind(box,title or 'error.title','setWindowTitle')
    bind(box,error_key(error))
    box.setDetailedText(details)
    box.setStandardButtons(QMessageBox.Ok)
    bind(box.button(QMessageBox.Ok),'ok')
    box.open();parent._error_dialog=box
