from dataclasses import dataclass, field
from enum import Enum


class FormatKind(str, Enum):
    VIDEO_ONLY = 'VIDEO_ONLY'
    AUDIO_ONLY = 'AUDIO_ONLY'
    MUXED = 'MUXED'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True)
class FormatProfile:
    label: str = ''
    format_id: str = ''
    video_format_id: str = ''
    audio_format_id: str = ''
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    dynamic_range: str | None = None
    hdr: bool | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    video_bitrate: float | None = None
    audio_bitrate: float | None = None
    container: str | None = None
    filesize: int | None = None
    filesize_approx: int | None = None
    kind: FormatKind = FormatKind.UNKNOWN
    is_video: bool = False
    is_audio: bool = False
    is_muxed: bool = False
    resolution: str | None = None
    video_codec_family: str = 'UNKNOWN'
    audio_codec_family: str = 'UNKNOWN'
    tbr: float | None = None
    vbr: float | None = None
    abr: float | None = None
    asr: float | None = None
    audio_channels: int | None = None
    ext: str | None = None
    protocol: str | None = None
    language: str | None = None
    duration: float | None = None
    quality_rank: tuple = ()
    # Raw metadata may contain signed URLs. Never serialize this model into logs.
    source_format: dict = field(default_factory=dict, repr=False, compare=False)


@dataclass(frozen=True)
class FormatSelection:
    mode: str
    video: FormatProfile | None = None
    audio: FormatProfile | None = None
    muxed: FormatProfile | None = None
    yt_dlp_format_expression: str = ''
    final_container: str | None = None
    estimated_size: int | None = None
    reason: str = ''
