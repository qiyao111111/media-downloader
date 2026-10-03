"""Adapter layer: pure-Python callbacks → Qt Signals for thread-safe GUI updates."""

from PySide6.QtCore import QObject, Signal


class DownloadBridge(QObject):
    """Bridges DownloadManager callbacks into Qt signals.

    Connect these signals to GUI slots for thread-safe updates.
    """

    # Download task signals
    progress = Signal(str, dict)            # task_id, progress data
    status_changed = Signal(str, str, str)  # task_id, old_status, new_status
    error = Signal(str, str)                # task_id, error message
    typed_error = Signal(str, object)

    # Info extraction signals
    info_extracted = Signal(str, dict)      # url, info_dict
    info_error = Signal(str, str)           # url, error message
    preview_failed = Signal(str, object)
    tools_ready = Signal(dict)
    health_ready = Signal(dict)
    update_ready = Signal(dict)
    task_added = Signal(dict)
    task_updated = Signal(dict)
    task_progress = Signal(dict)
    task_completed = Signal(dict)
    task_failed = Signal(dict)
    task_cancelled = Signal(dict)

    def on_event(self, name, record):
        getattr(self, name).emit(record)

    def on_progress(self, task_id: str, data: dict):
        self.progress.emit(task_id, data)

    def on_status_change(self, task_id: str, old_status, new_status):
        self.status_changed.emit(task_id, old_status.value, new_status.value)

    def on_error(self, task_id: str, exc: Exception):
        self.typed_error.emit(task_id, exc)
        self.error.emit(task_id, str(exc))

    def on_info_result(self, url: str, info: dict):
        self.info_extracted.emit(url, info)

    def on_info_error(self, url: str, error_msg: str):
        self.preview_failed.emit(url, error_msg)
        self.info_error.emit(url, str(error_msg))
