"""GUI application settings persistence (window state, language, last-used config)."""

import json
import os
from typing import Any

from core.credentials import persistent_options
from app.paths import PATHS
from services.atomic_storage import load_json, save_json

_SETTINGS_FILE = str(PATHS.config_dir/'app_settings.json')

_DEFAULTS: dict[str, Any] = {
    # App
    "language": "en",
    "theme": "light",
    "window_width": 960,
    "window_height": 720,
    "active_preset": "",
    "onboarding_complete": False,
    "debug_logging": False,

    # Download settings
    "download_path": str(PATHS.download_dir),
    "outtmpl": "",
    "proxy": "",
    "geo_verification_proxy": "",
    "ratelimit": "",
    "max_workers": 3,
    "concurrent_fragment_downloads": 1,
    "external_downloader": "",
    "sleep_interval": 0,
    "download_archive": "",

    # Format & quality
    "format": "",  # empty = dynamic source quality selection
    "format_sort": "",
    "merge_output_format": "",
    "audio_format": "mp3",
    "audio_quality": 5,

    # Video selection
    "noplaylist": False,
    "playlist_items": "",
    "min_filesize": "",
    "max_filesize": "",
    "date_range_start": "",
    "date_range_end": "",
    "match_filter": "",
    "max_downloads": 0,

    # Subtitles
    "writesubtitles": False,
    "write_auto_subs": False,
    "subtitleslangs": "",
    "sub_format": "best",
    "convert_subs": "",
    "embed_subs": False,

    # Metadata & thumbnails
    "writethumbnail": False,
    "embedthumbnail": False,
    "convert_thumbnails": "",
    "writedescription": False,
    "writeinfojson": False,
    "getcomments": False,

    # Post-processing
    "extract_audio": False,
    "embed_metadata": True,
    "embed_chapters": True,
    "remux_video": "",
    "recode_video": "",
    "sponsorblock_mark": "",
    "sponsorblock_remove": "",
    "split_chapters": False,
    "keep_video": False,
    "ffmpeg_location": "",
    "skip_download": False,

    # Authentication
    "cookiesfrombrowser": "None",
    "browser_profile": "",
    "retries": 10,
    "fragment_retries": 10,
    "cookiefile": "",
    "username": "",
    "password": "",
    "netrc": False,
}


class AppSettings:
    """Read / write application-level settings to a JSON file."""

    def __init__(self, path: str = _SETTINGS_FILE):
        self._path = path
        self._data: dict[str, Any] = dict(_DEFAULTS)
        self.load()

    def load(self):
        stored = load_json(self._path, {}, lambda value: isinstance(value, dict))
        clean = persistent_options(stored)
        self._data.update({key: value for key, value in clean.items()
                           if key in _DEFAULTS and type(value) is type(_DEFAULTS[key])})
        if not 1 <= self._data['max_workers'] <= 10:
            self._data['max_workers'] = _DEFAULTS['max_workers']
        if clean != stored:
            self.save()

    def save(self):
        save_json(self._path, persistent_options(self._data), lambda value: persistent_options(value) if isinstance(value,dict) else {})

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def update_from(self, opts: dict[str, Any]):
        """Bulk update settings from a dict (e.g., from settings panel)."""
        for key, value in opts.items():
            if key in _DEFAULTS:
                self._data[key] = value
