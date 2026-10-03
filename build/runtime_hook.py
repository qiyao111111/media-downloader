"""Preserve safe startup diagnostics even when a windowed build has no stderr."""
import sys
import traceback
from app.paths import PATHS
from core.credentials import redact


def startup_error(kind, value, tb):
    try:
        PATHS.logs_dir.mkdir(parents=True, exist_ok=True)
        text=''.join(traceback.format_tb(tb))+kind.__name__+': '+str(value)
        (PATHS.logs_dir/'startup-error.log').write_text(redact(text),encoding='utf-8')
    except OSError:
        pass


sys.excepthook=startup_error
