from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class TaskStatus(str, Enum):
    QUEUED = 'queued'
    PARSING = 'parsing'
    READY = 'ready'
    DOWNLOADING = 'downloading'
    POSTPROCESSING = 'postprocessing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    # Import compatibility only; no additional serialized states.
    PENDING = QUEUED
    RUNNING = PARSING
    CANCELED = CANCELLED

    @property
    def terminal(self):
        return self in (self.COMPLETED, self.FAILED, self.CANCELLED)

    @classmethod
    def normalize(cls, value):
        return cls({'pending': 'queued', 'running': 'parsing', 'canceled': 'cancelled',
                    'interrupted': 'cancelled'}.get(value, value))


def now():
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DownloadRecord:
    id: str
    url: str
    title: str = ''
    thumbnail: str = ''
    status: TaskStatus = TaskStatus.QUEUED
    progress: float = 0
    speed: float | None = None
    eta: float | None = None
    downloaded_bytes: int = 0
    total_bytes: int = 0
    quality: str = ''
    format_label: str = ''
    output_path: str = ''
    created_at: str = field(default_factory=now)
    started_at: str | None = None
    completed_at: str | None = None
    error: str = ''

    def transition(self, target):
        target = TaskStatus(target)
        if target == self.status:
            return
        order = (TaskStatus.QUEUED, TaskStatus.PARSING, TaskStatus.READY,
                 TaskStatus.DOWNLOADING, TaskStatus.POSTPROCESSING, TaskStatus.COMPLETED)
        playlist_cycle = self.status == TaskStatus.POSTPROCESSING and target == TaskStatus.DOWNLOADING
        if self.status.terminal or (not playlist_cycle and target not in (TaskStatus.FAILED, TaskStatus.CANCELLED)
                                   and order.index(target) != order.index(self.status) + 1):
            raise ValueError(f'Invalid task transition: {self.status.value} -> {target.value}')
        self.status = target
        if target == TaskStatus.PARSING:
            self.started_at = now()
        if target.terminal:
            self.completed_at = now()
