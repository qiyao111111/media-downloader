"""Build yt-dlp option dicts from user input with YAML defaults as fallback."""

import os
import math
from dataclasses import dataclass
from functools import partial
from typing import Any

import yaml
from yt_dlp.utils import DateRange, match_filter_func, parse_bytes
from core.cookies_manager import cookie_options
from core.proxy_manager import proxy_options
from core.format_selector import normalize_formats, select_quality
from models.format import FormatSelection
from app.paths import PATHS
from core.runtime_manager import runtime_options


@dataclass(frozen=True)
class QualitySelector:
    """Pickleable Windows worker callback; yt-dlp still assembles/downloads streams."""
    target: str | int = 'best'
    container: str | None = None

    def __call__(self, context):
        import yt_dlp
        from core.credentials import SafeLogger
        selection = select_quality(normalize_formats(context.get('formats')), self.target)
        # Reuse the native expression compiler and merger metadata, without extraction.
        with yt_dlp.YoutubeDL({'format': selection.yt_dlp_format_expression,
                              'merge_output_format': self.container or selection.final_container,
                              'logger': SafeLogger(), 'quiet': True}, auto_init=False) as compiler:
            yield from compiler.format_selector(context)


def _retry_delay(seconds, n):
    return seconds


def _match_filter(filters, info, incomplete=False):
    return match_filter_func(filters)(info, incomplete=incomplete)

_YDL_YAML = str(PATHS.resources_dir/'configs/yt-dlp.yml')


def _load_yaml_defaults() -> dict[str, Any]:
    """Load base defaults from yt-dlp.yml."""
    try:
        with open(_YDL_YAML, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f.read())
        return data.get("default", {}) if data else {}
    except FileNotFoundError:
        return {}


def build_opts(user_opts: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge YAML defaults with user-supplied options.

    Pipeline: merge → postprocessors → special fields → clean.
    """
    defaults = _load_yaml_defaults()
    # Always enable resume / partial download support
    defaults.setdefault("continuedl", True)
    inputs = dict(user_opts or {})
    if 'download_path' in inputs:
        path = inputs.pop('download_path')
        if path:
            inputs['paths'] = {'home': path}
    if 'embed_subs' in inputs:
        inputs['embedsubtitles'] = inputs.pop('embed_subs')
    selection = inputs.pop('format_selection', None)
    target = inputs.pop('quality_target', None)
    if selection is not None:
        if not isinstance(selection, FormatSelection):
            raise ValueError('format_selection must be a FormatSelection')
        inputs['format'] = selection.yt_dlp_format_expression
        if not inputs.get('merge_output_format'):
            inputs['merge_output_format'] = selection.final_container
    elif target is not None or not inputs.get('format'):
        inputs['format'] = QualitySelector(target if target is not None else
                                          ('audio' if inputs.get('extract_audio') else 'best'),
                                          inputs.get('merge_output_format') or None)
    for key in ('max_workers', 'theme', 'language', 'window_width', 'window_height', 'active_preset', 'quality_label', 'browser_profile'):
        inputs.pop(key, None)
    merged = runtime_options({**defaults, **inputs})
    merged.setdefault('proxy', '')  # Blank GUI proxy means direct, not inherited system proxy.
    for key in ('proxy', 'geo_verification_proxy'):
        if key in merged:
            merged.update(proxy_options(merged[key], key))
    merged = _build_postprocessors(merged)
    merged = _convert_special_fields(merged)
    merged = _convert_api_types(merged)
    return _clean(merged)


def _convert_api_types(opts):
    for key in ('ratelimit', 'min_filesize', 'max_filesize', 'buffersize', 'http_chunk_size'):
        value = opts.get(key)
        if value == '':
            continue
        if isinstance(value, str) and value.strip():
            opts[key] = parse_bytes(value)
            if opts[key] is None:
                raise ValueError(f"Invalid byte size for {key}")
        if opts.get(key) is not None and (isinstance(opts[key], bool) or not isinstance(opts[key], (int, float))
                                         or not math.isfinite(opts[key]) or opts[key] < 0):
            raise ValueError(f"Invalid byte size for {key}")
        if key in ('ratelimit', 'buffersize') and opts.get(key) == 0:
            raise ValueError(f"{key} must be greater than zero")
    for key in ('retries', 'fragment_retries', 'extractor_retries', 'concurrent_fragment_downloads',
                'playliststart', 'playlistend', 'skip_playlist_after_errors'):
        value = opts.get(key)
        if value is None or value == '':
            continue
        if value in ('infinite', float('inf')) and key.endswith('retries'):
            opts[key] = float('inf')
            continue
        number = float(value)
        minimum = 1 if key in ('concurrent_fragment_downloads', 'playliststart', 'playlistend') else 0
        if isinstance(value, bool) or not math.isfinite(number) or not number.is_integer() or number < minimum:
            raise ValueError(f"Invalid integer for {key}")
        opts[key] = int(number)
    for key in ('socket_timeout', 'sleep_interval', 'max_sleep_interval'):
        value = opts.get(key)
        if value is not None and value != '':
            number = float(value)
            if isinstance(value, bool) or not math.isfinite(number) or number < 0 or (key == 'socket_timeout' and number == 0):
                raise ValueError(f"Invalid duration for {key}")
            opts[key] = number
    if 'retry_sleep_functions' in opts:
        opts['retry_sleep_functions'] = dict(opts['retry_sleep_functions'])
    for kind, value in opts.get('retry_sleep_functions', {}).items():
        if not callable(value):
            seconds = float(value)
            if not math.isfinite(seconds) or seconds < 0:
                raise ValueError('Invalid retry delay')
            opts['retry_sleep_functions'][kind] = partial(_retry_delay, seconds)
    return opts


def _build_postprocessors(opts: dict[str, Any]) -> dict[str, Any]:
    """Assemble the postprocessors list from high-level flags."""
    pps: list[dict] = list(opts.get("postprocessors", []))

    # Extract audio
    if opts.pop("extract_audio", False):
        audio_fmt = opts.pop("audio_format", "mp3")
        audio_quality = opts.pop("audio_quality", 5)
        pps.append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_fmt,
            "preferredquality": str(audio_quality),
        })
    else:
        opts.pop("audio_format", None)
        opts.pop("audio_quality", None)

    # Embed thumbnail
    if opts.pop("embedthumbnail", False):
        if not opts.get("writethumbnail"):
            opts["writethumbnail"] = True
        pps.append({"key": "EmbedThumbnail"})

    # Convert thumbnails
    convert_thumb = opts.pop("convert_thumbnails", "")
    if convert_thumb:
        pps.append({
            "key": "FFmpegThumbnailsConvertor",
            "format": convert_thumb,
        })

    # Embed subtitles
    if opts.get("embedsubtitles"):
        pps.append({"key": "FFmpegEmbedSubtitle"})

    # Convert subtitles
    convert_subs = opts.pop("convert_subs", "")
    if convert_subs:
        pps.append({
            "key": "FFmpegSubtitlesConvertor",
            "format": convert_subs,
        })

    metadata = opts.pop("embed_metadata", False)
    chapters = opts.pop("embed_chapters", False)
    if metadata or chapters:
        pps.append({"key": "FFmpegMetadata", "add_metadata": metadata, "add_chapters": chapters})

    # Remux video (change container without re-encoding)
    remux = opts.pop("remux_video", "")
    if remux:
        pps.append({
            "key": "FFmpegVideoRemuxer",
            "preferedformat": remux,
        })

    # Recode video (re-encode)
    recode = opts.pop("recode_video", "")
    if recode:
        pps.append({
            "key": "FFmpegVideoConvertor",
            "preferedformat": recode,
        })

    # SponsorBlock
    sb_mark = opts.pop("sponsorblock_mark", "")
    sb_remove = opts.pop("sponsorblock_remove", "")
    if sb_mark or sb_remove:
        sb_opts: dict[str, Any] = {"key": "SponsorBlock"}
        if sb_mark:
            sb_opts["categories"] = [c.strip() for c in sb_mark.split(",")]
        if sb_remove:
            sb_opts["categories"] = [c.strip() for c in sb_remove.split(",")]
        pps.append(sb_opts)
        pps.append({"key": "ModifyChapters", "remove_sponsor_segments":
                    [c.strip() for c in sb_remove.split(",")] if sb_remove else []})

    # Split chapters
    if opts.pop("split_chapters", False):
        pps.append({"key": "FFmpegSplitChapters"})

    if pps:
        opts["postprocessors"] = pps

    return opts


def _convert_special_fields(opts: dict[str, Any]) -> dict[str, Any]:
    """Convert GUI-friendly values to yt-dlp expected types."""
    opts.update(cookie_options(opts.pop('cookiesfrombrowser', None), opts.pop('cookiefile', '')))

    # subtitleslangs: ensure list
    langs = opts.get("subtitleslangs")
    if isinstance(langs, str):
        opts["subtitleslangs"] = [s.strip() for s in langs.split(",") if s.strip()]

    # format_sort: string → list
    fmt_sort = opts.get("format_sort")
    if isinstance(fmt_sort, str) and fmt_sort.strip():
        opts["format_sort"] = [s.strip() for s in fmt_sort.split(",") if s.strip()]
    elif not fmt_sort:
        opts.pop("format_sort", None)

    # write_auto_subs → writeautomaticsub
    if opts.pop("write_auto_subs", False):
        opts["writeautomaticsub"] = True

    # sub_format → subtitlesformat
    sub_fmt = opts.pop("sub_format", "")
    if sub_fmt and sub_fmt != "best":
        opts["subtitlesformat"] = sub_fmt

    # merge_output_format
    merge_fmt = opts.get("merge_output_format")
    if not merge_fmt:
        opts.pop("merge_output_format", None)

    # ffmpeg_location
    ffmpeg_loc = opts.pop("ffmpeg_location", "")
    if ffmpeg_loc:
        opts["ffmpeg_location"] = ffmpeg_loc

    # download_archive
    archive = opts.pop("download_archive", "")
    if archive:
        opts["download_archive"] = archive

    # date range
    date_start = opts.pop("date_range_start", "")
    date_end = opts.pop("date_range_end", "")
    if date_start or date_end:
        opts["daterange"] = DateRange(date_start or None, date_end or None)

    # match_filter
    match_filter = opts.pop("match_filter", "")
    if match_filter:
        if callable(match_filter):
            opts["match_filter"] = match_filter
        else:
            filters = [match_filter] if isinstance(match_filter, str) else match_filter
            match_filter_func(filters)  # Validate before enqueueing.
            opts["match_filter"] = partial(_match_filter, filters)

    # max_downloads — remove unless explicitly set to a meaningful value (>= 2)
    # value of 0 = no limit, 1 = breaks thumbnail/subtitle downloads
    max_dl = opts.pop("max_downloads", 0)
    if isinstance(max_dl, int) and max_dl >= 2:
        opts["max_downloads"] = max_dl

    # sleep_interval
    sleep = opts.pop("sleep_interval", 0)
    if sleep:
        opts["sleep_interval"] = sleep

    # external_downloader
    ext_dl = opts.pop("external_downloader", "")
    if ext_dl and ext_dl != "none":
        opts["external_downloader"] = {"default": ext_dl}

    # keep_video
    if opts.get("keep_video"):
        opts["keepvideo"] = opts.pop("keep_video")
    else:
        opts.pop("keep_video", None)

    # netrc
    if opts.pop("netrc", False):
        opts["usenetrc"] = True

    # Clean up GUI-only keys that yt-dlp doesn't understand
    for gui_key in [
        "theme", "active_preset", "window_width", "window_height",
        "language", "download_path", "embed_subs",
    ]:
        opts.pop(gui_key, None)

    return opts


def _clean(opts: dict[str, Any]) -> dict[str, Any]:
    """Remove None and empty-string values. Preserve False booleans."""
    cleaned = {}
    for key, value in opts.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip() and key != 'proxy':
            continue
        if isinstance(value, (dict, list)) and len(value) == 0:
            continue
        cleaned[key] = value
    return cleaned
