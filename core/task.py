import threading
import uuid
from copy import deepcopy
from typing import Any, Callable, Optional

from core.runtime import DownloadCancelled, run_ydl, map_error
from models.download import DownloadRecord, TaskStatus


class DownloadTask:
    """Wraps a single yt-dlp download with status tracking and progress callbacks.

    Callbacks (all optional):
        on_progress(task_id, data)  – called by yt-dlp progress_hooks
        on_status_change(task_id, old_status, new_status)
        on_error(task_id, exception)
    """

    def __init__(
        self,
        url: str,
        ydl_opts: dict[str, Any],
        *,
        on_progress: Optional[Callable] = None,
        on_status_change: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        selection=None, title='',
    ):
        self.id: str = uuid.uuid4().hex[:8]
        self.url = url
        self.ydl_opts = deepcopy(ydl_opts)
        self.record = DownloadRecord(self.id, url)
        self.selection = selection
        self.record.title = title
        if selection:
            self.record.quality = (selection.video or selection.muxed or selection.audio).label
            self.record.format_label = selection.yt_dlp_format_expression
        self._cancel_event = threading.Event()
        self._error: Optional[Exception] = None
        self.output_files: list[str] = []
        self._run_lock = threading.Lock()

        self._on_progress = on_progress
        self._on_status_change = on_status_change
        self._on_error = on_error


    # -- Properties ----------------------------------------------------------

    @property
    def status(self) -> TaskStatus:
        return self.record.status

    @property
    def error(self) -> Optional[Exception]:
        return self._error

    # -- Control -------------------------------------------------------------

    def cancel(self):
        """Request cancellation. Safe to call from any thread."""
        self._cancel_event.set()
        if self._run_lock.acquire(blocking=False):
            try:
                if self.status == TaskStatus.QUEUED:
                    self._set_status(TaskStatus.CANCELLED)
            finally:
                self._run_lock.release()

    # -- Execution (called in worker thread) ---------------------------------

    def run(self):
        """Execute the download. Blocks until done / failed / canceled."""
        if not self._run_lock.acquire(blocking=False):
            return
        if self.status != TaskStatus.PENDING:
            self._run_lock.release()
            return
        self._set_status(TaskStatus.RUNNING)
        try:
            self.output_files = run_ydl(self.url, self.ydl_opts, self._cancel_event, self._progress_hook, self._postprocess_hook)
            if self._cancel_event.is_set():
                self._set_status(TaskStatus.CANCELED)
            else:
                self._advance_download()
                self._set_status(TaskStatus.POSTPROCESSING)
                self.record.output_path = self.output_files[0] if self.output_files else ''
                self.record.progress = 100
                self._set_status(TaskStatus.COMPLETED)

        except DownloadCancelled:
            self._set_status(TaskStatus.CANCELED)
        except Exception as exc:
            if self._cancel_event.is_set():
                self._set_status(TaskStatus.CANCELED)
            else:
                self._error = map_error(exc)
                self.record.error = str(self._error)
                self._set_status(TaskStatus.FAILED)
                if self._on_error:
                    self._on_error(self.id, self._error)
        finally:
            self._run_lock.release()

    # -- Internal ------------------------------------------------------------

    def _set_status(self, new: TaskStatus):
        old = self.status
        if old == new:
            return
        self.record.transition(new)
        if self._on_status_change:
            self._on_status_change(self.id, old, new)

    def _progress_hook(self, data: dict):
        if self._cancel_event.is_set():
            raise DownloadCancelled()
        info = data.get('info_dict', {})
        self.record.title = info.get('title') or self.record.title
        self.record.thumbnail = info.get('thumbnail') or self.record.thumbnail
        self.record.format_label = self.record.format_label or info.get('format_id', '')
        if info.get('height') and self.selection is None:
            from core.format_selector import normalize_format
            self.record.quality = normalize_format(info).label
        if data.get('status') == 'ready' and self.status == TaskStatus.PARSING:
            self._set_status(TaskStatus.READY)
        elif data.get('status') in ('downloading', 'finished'):
            self._advance_download()
            if self.status == TaskStatus.POSTPROCESSING:
                self._set_status(TaskStatus.DOWNLOADING)
        self.record.downloaded_bytes = data.get('downloaded_bytes', self.record.downloaded_bytes)
        self.record.total_bytes = data.get('total_bytes') or data.get('total_bytes_estimate') or self.record.total_bytes
        self.record.speed, self.record.eta = data.get('speed'), data.get('eta')
        if self.record.total_bytes:
            self.record.progress = min(100, 100 * self.record.downloaded_bytes / self.record.total_bytes)
        if self._on_progress:
            self._on_progress(self.id, data)

    def _advance_download(self):
        if self.status == TaskStatus.PARSING:
            self._set_status(TaskStatus.READY)
        if self.status == TaskStatus.READY:
            self._set_status(TaskStatus.DOWNLOADING)

    def _postprocess_hook(self, data):
        if self._cancel_event.is_set():
            raise DownloadCancelled()
        if data.get('postprocessor') != 'Ready' and data.get('status') == 'started':
            self._advance_download()
            self._set_status(TaskStatus.POSTPROCESSING)
