# B2 Selection Policy

## Video

Eligible video-only streams are preferred. Muxed streams are a fallback. Lexicographic comparison uses:

1. Actual height, then actual width. Missing dimensions count as zero; width assists when height is missing. No numeric ceiling or format-ID lookup table exists.
2. FPS, including fractional values and values above 60/120.
3. Dynamic range: reliable HDR/HDR10/HLG/DV above SDR, then UNKNOWN. HDR families share a rank; none is claimed universally superior. HDR10+ is grouped into HDR10. Codec strings never establish HDR.
4. Codec tie-break: AV1 > VP9 > H265 > H264 > VP8 > OTHER > UNKNOWN. This is an explicit default preference, not a perceptual-quality guarantee. It cannot override dimensions, FPS or HDR.
5. vbr, or tbr for video-only. A muxed total bitrate is not assumed to be video bitrate.
6. Known/estimated size.
7. MP4, WebM, MKV extension preference as the last compatibility tie-break; unknown extensions follow.

An identifier only stabilizes otherwise identical ties, never determines quality. Missing fields reduce confidence/rank rather than creating synthetic resolution/FPS/HDR. Dimensions are not read from a title, format note or free-text resolution. Exact 1440/2160/4320 heights get 2K/4K/8K labels; all other heights show the real number, including 8640P. Width differences are retained.

HDR and SDR variants both remain available. Deduplication keys include width, height, FPS, dynamic range, codec family, container, ext and kind. The best member of an otherwise equivalent group represents that group. Explicit extractor metadata marking DRM, DAMAGED or AI-upscaled excludes the representation; no fixed IDs are involved.

## Audio

Audio-only is preferred; muxed is a fallback. Within that pool: extractor language/original-track preference, no explicitly marked DRC processing, abr (or audio-only tbr), sample rate, channel count, codec (Opus > AAC > Vorbis > MP3 > OTHER > UNKNOWN), then size. Unspecified language preference is -1. Missing abr in muxed media is not replaced with its combined video bitrate.

Real testing exposed 251-drc at 130.583 kb/s versus uncompressed-dynamics 251 at 130.468 kb/s. The final policy prefers a track without an explicit DRC marker before comparing these rates; it does not infer DRC from a fixed format ID. This preserves original dynamics. Codec preference is a heuristic: bitrate across codecs is not a perceptual equivalence measure, and the policy does not claim it is. Explicit target selection remains available.

## Combination and estimates

Prefer a valid video-only + audio-only pair. Otherwise choose best valid muxed. With no valid video return NoPlayableVideo; with video but no usable audio/muxed return NoPlayableAudio. Audio-only mode never requires video. An explicit video-only target requires audio-only and cannot silently fall back to a different target.

Size precedence: filesize, filesize_approx, then kb/s × 1000 / 8 × duration. Unknown duration/rate returns None; overflow returns None. A split estimate is returned only when both components are known. Container overhead is not included.

The reason states the chosen label and decision priorities. It contains no source URL, headers, cookies or proxy credentials. No scale, FPS filter, tone mapping or video encoder is introduced. Custom format_sort applies on the native Custom path; the documented dynamic policy controls Best Quality.
