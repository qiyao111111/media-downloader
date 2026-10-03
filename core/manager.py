import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Optional

from core.task import DownloadTask, TaskStatus
from core.runtime import DownloadCancelled, run_ydl
from core.credentials import redact
from core.option_builder import build_opts
from dataclasses import asdict
from core.format_selector import normalize_formats, build_quality_options, select_quality
from core.runtime_manager import validate_download


class DownloadManager:
    """Manages a queue of DownloadTasks with concurrent execution.

    Pure-Python callback interface – no Qt dependency.

    Callbacks (all optional):
        on_progress(task_id, data)
        on_status_change(task_id, old_status, new_status)
        on_error(task_id, exception)
    """

    def __init__(
        self,
        max_workers: int = 3,
        *,
        on_progress: Optional[Callable] = None,
        on_status_change: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_event: Optional[Callable] = None,
    ):
        self._max_workers = max_workers
        self._on_progress = on_progress
        self._on_status_change = on_status_change
        self._on_error = on_error
        self._on_event = on_event

        self._tasks: dict[str, DownloadTask] = {}
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._preview_cancel = threading.Event()

    # -- Public API ----------------------------------------------------------

    def add_task(self, url: str, ydl_opts: dict[str, Any], *, selection=None, title='') -> str:
        """Create and enqueue a download task. Returns the task id."""
        task = DownloadTask(
            url,
            ydl_opts,
            on_progress=self._progress,
            on_status_change=self._status,
            on_error=self._on_error,
            selection=selection, title=title,
        )
        with self._lock:
            if any(t.url == url and not t.status.terminal
                   for t in self._tasks.values()):
                raise ValueError('This URL already has an active download')
            self._tasks[task.id] = task
        self._emit('task_added', task)
        self._executor.submit(task.run)
        return task.id

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task. Returns True if the task was found."""
        with self._lock:
            task = self._tasks.get(task_id)
        if task is None:
            return False
        task.cancel()
        return True

    def cancel_all(self):
        """Cancel every active task."""
        with self._lock:
            tasks = list(self._tasks.values())
        for task in tasks:
            if not task.status.terminal:
                task.cancel()

    @staticmethod
    def build_options(inputs):
        return build_opts(inputs)

    @staticmethod
    def quality_options(info):
        return build_quality_options(normalize_formats(info.get('formats'), info.get('duration')))

    @staticmethod
    def preview_formats(info):
        return normalize_formats(info.get('formats'), info.get('duration'))

    def inspect_tools(self, location, on_result):
        def check():
            from core.ffmpeg_utils import discover, version
            result = {}
            for tool in ('ffmpeg', 'ffprobe'):
                result[tool] = discover(tool, location)
                try:
                    result[tool + '_version'] = version(tool, location) or 'Not detected'
                except Exception as exc:
                    result[tool + '_version'] = redact(exc)
            on_result(result)
        self._executor.submit(check)

    @staticmethod
    def selection(info, target='best'):
        return select_quality(normalize_formats(info.get('formats'), info.get('duration')), target)

    def prepare_download(self, inputs, info, target='best'):
        inputs = dict(inputs)
        # A playlist's formats must be resolved independently for every entry.
        if info.get('_type') == 'playlist' or inputs.get('format'):
            return build_opts(inputs), None
        selection = self.selection(info, target)
        inputs.pop('quality_target', None)
        inputs['format_selection'] = selection
        options = build_opts(inputs)
        validate_download(options, selection)
        return options, selection

    def runtime_health(self, location, download_dir, on_result):
        from core.runtime_manager import health
        self._executor.submit(lambda: on_result(health(location, download_dir)))

    def check_runtime_update(self, on_result):
        from core.runtime_manager import check_update
        def check():
            try:on_result(check_update())
            except Exception as exc:on_result({'error':redact(exc)})
        self._executor.submit(check)

    def retry_task(self, task_id, options=None):
        task = self.get_task(task_id)
        if task is None or not task.status.terminal:
            raise ValueError('Only a finished task can be retried')
        return self.add_task(task.url, options or task.ydl_opts, selection=task.selection, title=task.record.title)

    def remove_task(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            return False
        task.cancel()
        # Keep an active worker tracked until cancellation has finished.
        if task.status.terminal:
            with self._lock:
                self._tasks.pop(task_id, None)
        return True

    def configure_workers(self, count):
        if not isinstance(count, int) or not 1 <= count <= 10:
            raise ValueError('Concurrent downloads must be between 1 and 10')
        if count == self._max_workers:
            return
        with self._lock:
            if any(not t.status.terminal for t in self._tasks.values()):
                raise ValueError('Change concurrent downloads after active tasks finish')
            old = self._executor
            self._executor = ThreadPoolExecutor(max_workers=count)
            self._max_workers = count
        old.shutdown(wait=False)

    def _emit(self, event, task):
        if self._on_event and task is not None:
            self._on_event(event, asdict(task.record))

    def _progress(self, task_id, data):
        if self._on_progress:
            self._on_progress(task_id, data)
        self._emit('task_progress', self.get_task(task_id))

    def _status(self, task_id, old, new):
        if self._on_status_change:
            self._on_status_change(task_id, old, new)
        task = self.get_task(task_id)
        self._emit('task_updated', task)
        if new.terminal:
            self._emit('task_' + new.value, task)

    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        with self._lock:
            return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[DownloadTask]:
        with self._lock:
            return list(self._tasks.values())

    def remove_finished(self):
        """Remove completed / failed / canceled tasks from the list."""
        terminal = {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED}
        with self._lock:
            self._tasks = {
                tid: t for tid, t in self._tasks.items() if t.status not in terminal
            }

    def extract_info(
        self,
        url: str,
        on_result: Callable,
        on_error: Callable,
        ydl_opts: dict[str, Any] | None = None,
    ):
        """Submit an info extraction job (no download).

        Calls on_result(url, info_dict) or on_error(url, error_msg).
        """
        def _run():
            try:
                options = dict(ydl_opts or {})
                options.setdefault('extract_flat', 'in_playlist')
                info = run_ydl(url, options, self._preview_cancel, preview=True)
                on_result(url, info)
            except DownloadCancelled:
                pass
            except Exception as e:
                on_error(url, e)

        self._executor.submit(_run)

    def shutdown(self, wait: bool = True):
        """Cancel all tasks and shut down the thread pool."""
        self.cancel_all()
        self._preview_cancel.set()
        self._executor.shutdown(wait=wait)
