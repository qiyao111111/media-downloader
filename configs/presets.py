"""Built-in and user-defined download presets."""

import json
import os
from typing import Any

from core.credentials import persistent_options
from models.settings import DownloadPreset
from app.paths import PATHS
from services.atomic_storage import load_json, save_json

_USER_PRESETS_FILE = str(PATHS.config_dir/'user_presets.json')

BUILTIN_PRESETS: dict[str, dict[str, Any]] = {
    "Best MP4": {
        "extract_audio": False,
        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
        "merge_output_format": "mp4",
        "embed_metadata": True,
        "embed_chapters": True,
    },
    "720p": {
        "extract_audio": False,
        "format": "bv*[height<=720]+ba/b[height<=720]",
        "merge_output_format": "mp4",
    },
    "1080p": {
        "extract_audio": False,
        "format": "bv*[height<=1080]+ba/b[height<=1080]",
        "merge_output_format": "mp4",
    },
    "Audio MP3": {
        "format": "ba",
        "extract_audio": True,
        "audio_format": "mp3",
        "audio_quality": 0,
    },
    "Audio FLAC": {
        "format": "ba",
        "extract_audio": True,
        "audio_format": "flac",
    },
    "With Subtitles": {
        "extract_audio": False,
        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
        "writesubtitles": True,
        "write_auto_subs": True,
        "subtitleslangs": "en,zh-Hans",
        "embedsubtitles": True,
        "convert_subs": "srt",
        "merge_output_format": "mkv",
    },
}


class PresetManager:
    """Manages built-in and user-defined presets."""

    def __init__(self, path: str = _USER_PRESETS_FILE):
        self._path = path
        self._user_presets: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self):
        stored = load_json(self._path, {}, lambda value: isinstance(value, dict))
        self._user_presets = {name: persistent_options(opts) for name, opts in stored.items() if isinstance(opts, dict)}
        if self._user_presets != stored:self._save()

    def _save(self):
        save_json(self._path, {name: persistent_options(opts) for name, opts in self._user_presets.items()},
                  lambda value: {name:persistent_options(opts) for name,opts in value.items() if isinstance(opts,dict)} if isinstance(value,dict) else {})

    def get_all(self) -> dict[str, dict[str, Any]]:
        """Return all presets (built-in + user), user presets override built-in."""
        merged = dict(BUILTIN_PRESETS)
        merged.update(self._user_presets)
        return merged

    def get_builtin_names(self) -> list[str]:
        return list(BUILTIN_PRESETS.keys())

    def get_user_names(self) -> list[str]:
        return list(self._user_presets.keys())

    def get(self, name: str) -> dict[str, Any] | None:
        if name in self._user_presets:
            return self._user_presets[name]
        return BUILTIN_PRESETS.get(name)

    def save_user_preset(self, name: str, opts: dict[str, Any]):
        self._user_presets[name] = persistent_options(DownloadPreset(opts).download_options())
        self._save()

    def delete_user_preset(self, name: str) -> bool:
        if name in self._user_presets:
            del self._user_presets[name]
            self._save()
            return True
        return False
