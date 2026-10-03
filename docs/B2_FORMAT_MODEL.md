# B2 Format Model

Date: 2026-10-02. Base: `744de1ecc0ecfa233f36a189f91959b2dd43f46e`.
Branch: `codex/b2-format-selector`; starting worktree was clean. Master and B1 remain unchanged.

## Public contract

`models/format.py` contains frozen `FormatProfile`, `FormatKind`, and `FormatSelection` dataclasses. `core/format_selector.py` owns normalization, selection, option deduplication, size estimation and container recommendation. No Qt or network calls occur there.

| Fields | Meaning |
|---|---|
| format_id, label | Source identifier and human-readable label; IDs never imply resolution |
| kind, is_video, is_audio, is_muxed | VIDEO_ONLY / AUDIO_ONLY / MUXED / UNKNOWN, from codec fields |
| width, height, resolution, fps | Positive finite source values; resolution is derived from actual dimensions |
| dynamic_range, hdr | SDR/HDR/HDR10/HLG/DV/UNKNOWN; UNKNOWN has hdr=None |
| video_codec, video_codec_family | Raw codec and AV1/VP9/H264/H265/VP8/OTHER/UNKNOWN |
| audio_codec, audio_codec_family | Raw codec and OPUS/AAC/MP3/VORBIS/OTHER/UNKNOWN |
| tbr, vbr, abr, asr, audio_channels | Positive finite rates/channels; video_bitrate/audio_bitrate retained as compatibility aliases |
| container, ext | Source container and filename extension, independent of codec |
| filesize, filesize_approx, duration | Source sizes and duration used for estimates |
| protocol, language | Optional source metadata |
| quality_rank | Normalized diagnostic rank tuple |
| video_format_id, audio_format_id | Stream identifiers according to codec presence |
| source_format | Original metadata copy, excluded from repr/equality; private, not a log payload |

`None`, zero, negative/nonfinite numbers, wrong types, missing dictionaries and unknown strings cannot crash normalization. Invalid scalar collections return an empty list. Missing codec knowledge remains UNKNOWN; an MP4 extension never implies H264/AAC. Storyboards, DRM, extractor-marked damaged and AI-upscaled representations are excluded from selectable quality options. Network accessibility is validated by yt-dlp during extraction/download, not guessed by the pure selector.

`FormatSelection` exposes mode (split/muxed/audio), video/audio/muxed profiles, exact yt_dlp_format_expression, final_container, estimated_size and reason. Error categories are NoFormats, NoPlayableVideo, NoPlayableAudio, InvalidTarget and UnsupportedSelection. Source identifiers containing expression syntax are rejected rather than interpolated unsafely.

## APIs and integration

- normalize_format(raw, duration=None), normalize_formats(raw_formats, duration=None)
- build_quality_options(profiles), deduplicate_quality_options(profiles)
- select_best_video(profiles), select_best_audio(profiles)
- select_best_combination(profiles), select_quality(profiles, target)
- recommend_final_container(selection), estimate_size(profile)

Targets are `best`, `audio`, an exact positive height, a real profile or a source format ID. Unavailable exact targets fail diagnostically; they never silently select a lower resolution. Best Quality is a mode, not a fictitious format row. Quality rows all come from the extracted formats. HDR/SDR, FPS, dimensions, codec families, containers and stream kinds remain distinct.

The option builder accepts `quality_target` or `format_selection`. A pickleable `QualitySelector` callback selects from the formats of the current native extraction, then reuses yt-dlp's own expression compiler and merger metadata. This avoids a second extraction inside a download and preserves native cookies/proxy/headers, retry, resume and cancellation. The compiler instance performs no extraction or downloads and receives no credentials. Preview and Download use the same callback/options. A precomputed selection can also be passed to the builder when its metadata context is still current.

The existing Preview table now displays labels and keeps the ID in an Advanced column. A selected row passes an opaque target through the settings panel into the builder; the UI never joins video/audio IDs. Edited raw expressions and existing presets remain Advanced/Custom. Blank format selects dynamic source quality; blank format with extract_audio selects independent best audio. Explicit `ba` remains native Custom behavior. Applying a format preset clears a transient quality target. Full B3 UI and persistent per-video quality choices are deferred.

Complexity: normalization/selection O(n); deduplication plus sorting O(n log n). No dependencies added. Never serialize `source_format` or use dataclasses.asdict(profile) for logging: it can contain signed media URLs and headers.
