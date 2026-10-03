# B2 Container Policy

Validated environment: Windows, FFmpeg/ffprobe 8.0 (Gyan essentials), yt-dlp 2026.8.19. Recommendations concern stream copy, not universal playback compatibility.

| Selected codecs | Default recommendation | Scope |
|---|---|---|
| H264 + AAC | MP4 | Conventional combination |
| AV1 + AAC | MP4 | FFmpeg supports muxing; playback requires AV1 support |
| H265 + AAC | MP4 | Codec/player support still varies |
| H264/H265/AV1 + Opus | MP4 | Supported by this FFmpeg baseline; some players do not support Opus-in-MP4 |
| VP9 + Opus, other combinations | MKV | Broad stream-copy container; WebM is also possible for compatible codec combinations |
| Existing muxed/audio-only | Source ext | Preserve source container unless user explicitly requests processing |

The same recommendation reaches yt-dlp's native format compiler through merge_output_format. An explicit user merge container wins. yt-dlp and FFmpeg retain final authority over muxing support; an unsupported explicit request may fail and is never repaired by silently transcoding. Older FFmpeg releases are not certified by B2; recommendations are not an exhaustive capability claim.

B1 found that this FFmpeg build can report an Opus packet-header diagnostic when probing its MKV output. AV1+Opus MP4 was already verified by B1 lossless remux; B2 therefore recommends native MP4 merge for this combination and verifies the final file directly. This does not imply MP4 is higher video quality. The selector has already chosen codecs and source quality before choosing the container.

The adapter only adds an FFmpeg-availability check before downloading selected split streams. yt-dlp continues to own Merger/postprocessing. No replacement FFmpeg engine, encoder, scale filter, FPS conversion, HDR-to-SDR or upscale command is added. Existing explicitly requested audio extraction/transcoding and Custom options remain supported.
