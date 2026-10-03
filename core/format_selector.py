"""Source metadata selection; no UI, network, transcoding or resolution ceiling."""
import math
import re
from dataclasses import replace

from models.errors import FormatError
from models.format import FormatKind as Kind, FormatProfile, FormatSelection


class FormatSelectionError(FormatError):
    def __init__(self, category, message=''):
        self.category = category
        super().__init__(f'{category}: {message}')


def _number(value, integer=False):
    try:
        number = float(value) if not isinstance(value, bool) else 0
        return (int(number) if integer else number) if math.isfinite(number) and number > 0 else None
    except (ValueError, TypeError, OverflowError):
        return None


def _text(value):
    return value.strip() if isinstance(value, str) and value.strip() else None


def _family(codec, audio=False):
    codec = (codec or '').lower()
    if codec in ('', 'none', 'unknown'):
        return 'UNKNOWN'
    families = (('OPUS', ('opus',)), ('AAC', ('mp4a', 'aac')), ('MP3', ('mp3',)),
                ('VORBIS', ('vorbis',))) if audio else (
        ('AV1', ('av01', 'av1')), ('VP9', ('vp9', 'vp09')), ('H264', ('avc1', 'avc3', 'h264')),
        ('H265', ('hev1', 'hvc1', 'hevc', 'h265')), ('VP8', ('vp8', 'vp08')))
    return next((family for family, prefixes in families if codec.startswith(prefixes)), 'OTHER')


def _range(value):
    value = (_text(value) or '').upper().replace(' ', '')
    return {'HDR10+': 'HDR10', 'DOLBYVISION': 'DV'}.get(value, value) if value in (
        'SDR', 'HDR', 'HDR10', 'HDR10+', 'HLG', 'DV', 'DOLBYVISION') else 'UNKNOWN'


def estimate_size(profile):
    if profile.filesize or profile.filesize_approx:
        return profile.filesize or profile.filesize_approx
    bitrate = profile.tbr or ((profile.vbr or 0) + (profile.abr or 0))
    size = bitrate * 1000 / 8 * profile.duration if bitrate and profile.duration else None
    return int(size) if size is not None and math.isfinite(size) else None


def video_rank(p):
    # Known height first; width resolves equal heights and assists incomplete metadata.
    return (p.height or 0, p.width or 0, p.fps or 0,
            {'UNKNOWN': 0, 'SDR': 1, 'HDR': 2, 'HDR10': 2, 'HLG': 2, 'DV': 2}[p.dynamic_range or 'UNKNOWN'],
            {'UNKNOWN': 0, 'OTHER': 1, 'VP8': 2, 'H264': 3, 'H265': 4, 'VP9': 5, 'AV1': 6}[p.video_codec_family],
            p.vbr or (p.tbr if p.kind == Kind.VIDEO_ONLY else 0) or 0,
            estimate_size(p) or 0, {'mp4': 3, 'webm': 2, 'mkv': 1}.get(p.ext, 0))


def audio_rank(p):
    # Respect extractor language/original-track preference before comparing encodes.
    preference = p.source_format.get('language_preference')
    try:
        preference = float(preference)
        if not math.isfinite(preference): preference = -1
    except (TypeError, ValueError, OverflowError):
        preference = -1
    note = (_text(p.source_format.get('format_note')) or '').upper()
    drc = bool(re.search(r'\bDRC\b', note)) or p.source_format.get('is_drc') is True
    return (preference, not drc, p.abr or (p.tbr if p.kind == Kind.AUDIO_ONLY else 0) or 0,
            p.asr or 0, p.audio_channels or 0,
            {'UNKNOWN': 0, 'OTHER': 1, 'MP3': 2, 'VORBIS': 3, 'AAC': 4, 'OPUS': 5}[p.audio_codec_family],
            estimate_size(p) or 0)


def _label(p):
    if not p.is_video:
        return ' · '.join(x for x in ('Audio' if p.is_audio else 'Unknown', p.audio_codec_family, p.ext) if x)
    size = f'{p.height}P' if p.height else (f'{p.width}px wide' if p.width else 'Unknown resolution')
    prefix = {1440: '2K', 2160: '4K', 4320: '8K'}.get(p.height)
    return ' · '.join(x for x in (prefix, size, f'{p.fps:g} FPS' if p.fps else None,
                                  p.video_codec_family, p.dynamic_range, p.ext) if x)


def normalize_format(raw, duration=None):
    raw = raw if isinstance(raw, dict) else {}
    v, a = _text(raw.get('vcodec')), _text(raw.get('acodec'))
    video = bool(v and v.lower() not in ('none', 'unknown', 'images'))
    audio = bool(a and a.lower() not in ('none', 'unknown'))
    kind = (Kind.MUXED if video and audio else Kind.VIDEO_ONLY if video and (a or '').lower() == 'none'
            else Kind.AUDIO_ONLY if audio and (v or '').lower() == 'none' else Kind.UNKNOWN)
    numbers = {k: _number(raw.get(k), k in ('width', 'height', 'filesize', 'filesize_approx', 'audio_channels'))
               for k in ('width', 'height', 'fps', 'tbr', 'vbr', 'abr', 'asr', 'audio_channels', 'filesize', 'filesize_approx')}
    dr = _range(raw.get('dynamic_range'))
    fid = raw.get('format_id')
    try:
        fid = str(fid) if isinstance(fid, (str, int)) and not isinstance(fid, bool) else ''
    except ValueError:
        fid = ''
    p = FormatProfile(format_id=fid, kind=kind, is_video=video, is_audio=audio, is_muxed=kind == Kind.MUXED,
                      video_format_id=fid if video else '', audio_format_id=fid if audio else '',
                      video_codec=v, audio_codec=a, video_codec_family=_family(v), audio_codec_family=_family(a, True),
                      dynamic_range=dr, hdr=None if dr == 'UNKNOWN' else dr != 'SDR',
                      container=_text(raw.get('container')) or _text(raw.get('ext')), ext=_text(raw.get('ext')),
                      protocol=_text(raw.get('protocol')), language=_text(raw.get('language')),
                      duration=_number(raw.get('duration')) or _number(duration), source_format=dict(raw),
                      video_bitrate=numbers['vbr'], audio_bitrate=numbers['abr'], **numbers)
    resolution = f'{p.width}×{p.height}' if p.width and p.height else (f'{p.height}P' if p.height else None)
    return replace(p, resolution=resolution, label=_label(p), quality_rank=video_rank(p) if video else audio_rank(p))


def normalize_formats(raw_formats, duration=None):
    if not isinstance(raw_formats, (list, tuple)):
        return []
    return [p if isinstance(p, FormatProfile) else normalize_format(p, duration) for p in raw_formats]


def _valid(p):
    note = (_text(p.source_format.get('format_note')) or '').upper()
    return bool(p.format_id and p.kind != Kind.UNKNOWN and not p.source_format.get('has_drm')
                and 'AI-UPSCALED' not in note and 'DAMAGED' not in note)


def _best(formats, primary, fallback, rank):
    valid = [p for p in formats if _valid(p)]
    candidates = [p for p in valid if p.kind == primary] or [p for p in valid if p.kind == fallback]
    return max(candidates, key=lambda p: (rank(p), p.format_id), default=None)


def select_best_video(formats):
    return _best(formats, Kind.VIDEO_ONLY, Kind.MUXED, video_rank)


def select_best_audio(formats):
    return _best(formats, Kind.AUDIO_ONLY, Kind.MUXED, audio_rank)


def deduplicate_quality_options(formats):
    groups = {}
    for p in formats:
        if not _valid(p) or not p.is_video: continue
        key = (p.width, p.height, p.fps, p.dynamic_range, p.video_codec_family, p.container, p.ext, p.kind)
        previous = groups.get(key)
        if previous is None or (video_rank(p), p.format_id) > (video_rank(previous), previous.format_id):
            groups[key] = p
    return sorted(groups.values(), key=lambda p: (video_rank(p), p.format_id), reverse=True)


def build_quality_options(formats):
    """Real video profiles only. 'Best Quality' is a mode, not a fabricated format."""
    return deduplicate_quality_options(formats)


def recommend_final_container(selection):
    if selection.muxed:
        return selection.muxed.ext
    v, a = selection.video, selection.audio
    if not v:
        return a.ext if a else None
    # Stream copy supported by the validated FFmpeg 8 baseline; player support differs.
    if a and v.video_codec_family in ('H264', 'H265', 'AV1') and a.audio_codec_family in ('AAC', 'OPUS'):
        return 'mp4'
    return 'mkv'


def _selection(mode, video=None, audio=None, muxed=None):
    profiles = [muxed] if muxed else [p for p in (video, audio) if p]
    if any(not re.fullmatch(r'[A-Za-z0-9_.:-]+', p.format_id) for p in profiles):
        raise FormatSelectionError('UnsupportedSelection', 'Format identifier cannot be represented safely')
    sizes = [estimate_size(p) for p in profiles]
    reason = ('Selected ' + (video or muxed or audio).label + '; '
              + ('resolution, width, FPS, HDR, codec, bitrate, size, container priority; separate audio: '
                 + audio.label + ' (language, original/non-DRC, bitrate, sample rate, channels, codec, size)'
                 if mode == 'split' else 'best valid muxed fallback' if mode == 'muxed' else 'independent audio ranking'))
    result = FormatSelection(mode=mode, video=video, audio=audio, muxed=muxed,
                             yt_dlp_format_expression='+'.join(p.format_id for p in profiles),
                             estimated_size=sum(sizes) if all(s is not None for s in sizes) else None,
                             reason=reason)
    return replace(result, final_container=recommend_final_container(result))


def select_best_combination(formats):
    if not formats: raise FormatSelectionError('NoFormats', 'No source formats')
    video, audio = select_best_video(formats), select_best_audio(formats)
    if video and audio and video.kind == Kind.VIDEO_ONLY and audio.kind == Kind.AUDIO_ONLY:
        return _selection('split', video=video, audio=audio)
    muxed = _best(formats, Kind.MUXED, Kind.MUXED, video_rank)
    if muxed: return _selection('muxed', muxed=muxed)
    if not video: raise FormatSelectionError('NoPlayableVideo', 'No valid video stream')
    raise FormatSelectionError('NoPlayableAudio', 'No valid audio stream or muxed fallback')


def select_quality(formats, target='best'):
    """Target: best/audio, positive exact height, or a real FormatProfile/format ID."""
    if not formats: raise FormatSelectionError('NoFormats', 'No source formats')
    if target == 'best': return select_best_combination(formats)
    if target == 'audio':
        audio = select_best_audio(formats)
        if not audio: raise FormatSelectionError('NoPlayableAudio', 'No valid audio')
        return _selection('audio', audio=audio)
    if isinstance(target, FormatProfile): target = target.format_id
    if isinstance(target, int) and not isinstance(target, bool) and target > 0:
        candidates = [p for p in formats if p.height == target and _valid(p)]
    elif isinstance(target, str):
        candidates = [p for p in formats if p.format_id == target and _valid(p)]
    else: candidates = []
    if not candidates: raise FormatSelectionError('InvalidTarget', 'Requested quality is not available')
    if len(candidates) == 1 and candidates[0].kind == Kind.AUDIO_ONLY:
        return _selection('audio', audio=candidates[0])
    chosen = select_best_video(candidates)
    if not chosen: raise FormatSelectionError('InvalidTarget', 'Target is not a video quality')
    if chosen.kind == Kind.MUXED: return _selection('muxed', muxed=chosen)
    audio = select_best_audio(formats)
    if not audio or audio.kind != Kind.AUDIO_ONLY:
        raise FormatSelectionError('NoPlayableAudio', 'Selected video needs an audio-only stream')
    return _selection('split', video=chosen, audio=audio)
