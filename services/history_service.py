"""Download history persistence – survives app restarts."""

import json
import os
import time
from typing import Any
from copy import deepcopy
from core.credentials import persistent_url, redact
from models.download import TaskStatus, now
from app.paths import PATHS
from services.atomic_storage import load_json, save_json

_HISTORY_FILE = str(PATHS.data_dir/'download_history.json') if PATHS.mode!='source' else str(PATHS.config_dir/'download_history.json')


class HistoryService:
    """Persists download task records to JSON."""

    def __init__(self, path: str = _HISTORY_FILE):
        self._path = path
        self._records: list[dict[str, Any]] = []
        self._load()

    def _load(self):
        records = load_json(self._path, [], lambda value: isinstance(value, list))
        self._records = [self._clean(r) for r in records if isinstance(r, dict) and r.get('task_id')]

    def _save(self):
        save_json(self._path, self._records, lambda value: [self._clean(r) for r in value if isinstance(r,dict)] if isinstance(value,list) else [])

    def add(self, task_id: str, url: str, title: str = ""):
        self.add_record({
            "task_id": task_id,
            "url": persistent_url(url),
            "title": title,
            "status": TaskStatus.QUEUED.value,
            "progress": 0,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

    @staticmethod
    def _clean(record):
        clean = {k: v for k, v in record.items() if k in ('task_id', 'url', 'title', 'quality', 'status',
                 'output_path', 'timestamp', 'date', 'progress', 'error')}
        clean['url'] = persistent_url(clean.get('url', ''))
        clean['error'] = redact(clean.get('error', ''))
        clean.setdefault('quality', '')
        clean.setdefault('output_path', '')
        clean.setdefault('date', clean.get('timestamp', now()))
        try:
            status = TaskStatus.normalize(clean.get('status', 'failed'))
            clean['status'] = status.value
        except ValueError:
            clean['status'] = TaskStatus.FAILED.value
        return clean

    def add_record(self, record):
        clean = self._clean(record)
        if not any(r['task_id'] == clean['task_id'] for r in self._records):
            self._records.append(clean)
            self._save()

    def update_record(self, task_id, **changes):
        for record in self._records:
            if record['task_id'] == task_id:
                record.update(self._clean({**record, **changes}))
                self._save()
                break

    def list_records(self):
        return deepcopy(self._records)

    def clear_history(self):
        self.clear_all()

    def update_status(self, task_id: str, status: str):
        self.update_record(task_id, status=status)

    def update_title(self, task_id: str, title: str):
        for r in self._records:
            if r["task_id"] == task_id:
                if not r.get("title"):
                    r["title"] = title
                    self._save()
                return

    def get_all(self) -> list[dict[str, Any]]:
        return self.list_records()

    def clear_completed(self):
        self._records = [r for r in self._records if not TaskStatus.normalize(r['status']).terminal]
        self._save()

    def delete(self, task_id: str):
        self._records = [r for r in self._records if r["task_id"] != task_id]
        self._save()

    def clear_all(self):
        self._records = []
        self._save()
