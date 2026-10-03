"""FFmpeg detection and utilities."""

import shutil
import json
import subprocess
from pathlib import Path
from functools import lru_cache
from core.runtime_manager import tool_path, NO_WINDOW


@lru_cache(maxsize=1)
def find_ffmpeg() -> str | None:
    """Return the path to ffmpeg if found, else None."""
    return tool_path('ffmpeg')


@lru_cache(maxsize=1)
def find_ffprobe() -> str | None:
    """Return the path to ffprobe if found, else None."""
    return tool_path('ffprobe')


def is_ffmpeg_available() -> bool:
    return find_ffmpeg() is not None


def get_default_format() -> str:
    """Select independent source streams, without a resolution ceiling."""
    return "bv+ba"


def discover(binary, location=''):
    return tool_path(binary, location)


def version(binary, location=''):
    path = discover(binary, location)
    if not path:
        return None
    return subprocess.check_output([path, '-version'], encoding='utf-8', errors='replace', timeout=10, creationflags=NO_WINDOW).splitlines()[0]


def validate_media(path, location=''):
    tool = discover('ffprobe', location)
    if not tool:
        raise FileNotFoundError('FFprobe is not available')
    probe = json.loads(subprocess.check_output([tool, '-v', 'error', '-show_streams', '-show_format',
                                              '-of', 'json', str(path)], timeout=30, creationflags=NO_WINDOW))
    if not probe.get('streams') or Path(path).stat().st_size == 0:
        raise ValueError('Final media has no streams or is empty')
    return probe
