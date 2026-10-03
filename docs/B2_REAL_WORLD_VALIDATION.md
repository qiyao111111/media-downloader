# B2 Real World Validation

Date: 2026-10-02. Windows / Python 3.13.13 / yt-dlp 2026.8.19 / FFmpeg 8.0.

The primary source is an actual 155-second 8K camera sample. Its real 1080P and 4K representations are tested as explicit targets; these rows do **not** claim the source is capped at 1080P or 4K. All format IDs below are observed test results, never constants in the selector.

| Quality / target | Video URL | Available highest | Formats | Selected video | Selected audio | Expression | Container | Result |
|---|---|---|---|---|---|---|---|---|
| 1080P target | https://www.youtube.com/watch?v=E86EwGT_c2M | 4320P | 53 | 399: 1920x1080, 30 FPS, av01.0.08M.08, SDR | 251: opus | 399+251 | mp4 | PASS: metadata/selection + full download/ffprobe |
| 4K target | https://www.youtube.com/watch?v=E86EwGT_c2M | 4320P | 53 | 401: 3840x2160, 30 FPS, av01.0.12M.08, SDR | 251: opus | 401+251 | mp4 | PASS: metadata/selection + full download/ffprobe |
| 8K Best Quality | https://www.youtube.com/watch?v=E86EwGT_c2M | 4320P | 53 | 571: 7680x4320, 30 FPS, av01.0.16M.08, SDR | 251: opus | 571+251 | mp4 | PASS: metadata/selection + full download/ffprobe + full decode |
| 8K60 HDR Best Quality | https://www.youtube.com/watch?v=hVvEISFw9w0 | 4320P | 70 | 702: 7680x4320, 60 FPS, av01.0.17M.10.0.110.09.16.09.0, HDR10 | 140: mp4a.40.2 | 702+140 | mp4 | PASS: metadata/selection only |

Additional native-best 4K source: https://www.youtube.com/watch?v=aqz-KE-bpKQ, observed 53 formats, maximum 2160P, selected 401+140 (3840x2160 AV1 60 FPS SDR + AAC), MP4 recommendation, metadata/selection PASS. Evidence: `D:\YouTube视频下载\B2-additional-sources.log`. The unrelated BaW_jenozKc candidate was unavailable and is not counted as a pass.

## Full 8K acceptance

The final policy downloaded full video-only 571 + audio-only 251, then yt-dlp/FFmpeg merged directly to MP4. No section limit, scale filter, frame-rate conversion, video encoder or tone mapping was configured. Final file exists and contains both video and audio. Full decode used `ffmpeg -v error -i FILE -fps_mode passthrough -enc_time_base:v demux -f null -`, without `-t` or section limits.

```json
{
  "file": "D:\\YouTube视频下载\\B2 evidence\\formats-final\\best_E86EwGT_c2M.mp4",
  "bytes": 614003516,
  "sha256": "6b69bb0265c2ede9b2ac86fff8576ae6ac35dc2e13934269ee06b88a966d1198",
  "duration": "154.781000",
  "video": {
    "width": 7680,
    "height": 4320,
    "codec_name": "av1",
    "pix_fmt": "yuv420p",
    "r_frame_rate": "5991/200",
    "avg_frame_rate": "5991/200",
    "duration": "154.732098",
    "color_transfer": "bt709"
  },
  "audio": {
    "codec_name": "opus",
    "sample_rate": "48000",
    "channels": 2,
    "duration": "154.781000"
  },
  "container": "mov,mp4,m4a,3gp,3g2,mj2",
  "decode_returncode": 0,
  "decode_error_bytes": 0
}
```

8K acceptance: **PASS**. Decode exit 0, error log 0 bytes. The source metadata reports 30 FPS; ffprobe exposes the actual fractional/variable timing, which is retained rather than converted to exactly 30.

1080P and 4K full files: 47,915,386 and 324,635,229 bytes respectively, AV1 yuv420p + Opus in MP4, 154.781 s. ffprobe r_frame_rate/avg_frame_rate both 5991/200 (~29.955); color transfer bt709. 4K was cancelled, resumed via the real task-table Retry action, and completed with both streams. Their probes are in desktop-final.

8K60/HDR metadata: 70 real formats, 54 distinct video quality options, selected native 7680x4320/60 FPS/AV1/HDR10. No full HDR download is claimed. Synthetic 8640P unit tests remain separate from real media evidence.

## Evidence and reproducibility

Root: `D:\YouTube视频下载\B2 evidence\`.

- `formats-final/results.json`: sanitized metadata, selected identifiers, expressions, containers and full download/decode result.
- `formats-final/ffprobe.json`, `acceptance.json`, `decode-progress.log`, `decode-errors.log`: final 8K verification.
- `desktop-final/desktop-results.json`, `probe-summary.json`, `1080p-ffprobe.json`, `4k-cancel-retry-ffprobe.json`: full 1080P/4K and regression results.
- `audio-retest/desktop-results.json`: successful same-source Audio Only retry after one HTTP 403.
- `gui/gui-results.json`: real application lifecycle/responsiveness check.

Reproduce with `tests/validate_b2_formats.py OUTPUT_DIRECTORY` and `tests/validate_b1_desktop.py OUTPUT_DIRECTORY --dynamic`. Output directories must be fresh to establish fresh transfers. Binary media, controlled cookie files and raw evidence stay outside Git. No personal browser cookies were read and no cookies/authorization/proxy passwords enter the reports.

Earlier development evidence in `formats` and `desktop` is retained separately and used a DRC-preferring policy; final-policy acceptance uses the `*-final` folders. See B2_REGRESSION.md for the retained transient 403 failure and retry. yt-dlp's existing missing-JS-runtime warning limits claims to formats returned in this environment; it does not create a software resolution ceiling.
