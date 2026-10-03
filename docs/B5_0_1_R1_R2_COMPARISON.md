# B5.0.1 FFmpeg r1 / r2 comparison

| Dimension | r1 | r2 |
|---|---|---|
| Version | 8.1.3-g330caae0c1-md-b43-r1 | 8.1.3-g330caae0c1-md-b43-r2 |
| Exact FFmpeg revision | 330caae0c1acccd2222edc52a05940c574561ce5 | 330caae0c1acccd2222edc52a05940c574561ce5 |
| Source archive | FFmpeg-330caae0c1acccd2222edc52a05940c574561ce5.tar.gz | Same exact archive |
| Archive SHA256 | 485bfaa6cdce46ba8e61b2866133d7118fc07f65d790a6295c31e6f0e2a62e71 | Same |
| Build recipe | Stable-tag build_native_runtime.py | Recipe from b9794ef, now adopted |
| Configure difference | r1 extra-version; ffmetadata disabled | r2 extra-version; built-in ffmetadata demuxer enabled |
| External libraries | dav1d, Opus, LAME, zlib, WebP, VPX, OpenH264 | Unchanged exact source pins |
| License configuration | --disable-gpl --disable-nonfree --disable-version3, shared FFmpeg | Same |
| Source patches | None | None |
| Encoder/muxer lists | B4.3 explicit lists | Unchanged |
| Behavioral fix | yt-dlp FFMETADATA chapter input rejected | Chapter embedding succeeds |

R1 audit uses the immutable stable-tag lock/recipe and existing B4.3/B5 evidence. The old local binary backup was removed during the earlier workspace cleanup; this run does not claim a fresh execution of r1. Historical expected hashes below are the exact stable-tag pins. No r1 provenance is inferred from an r2 filename.

R2 was freshly inspected using ffmpeg -version/-buildconf/-L and ffprobe -version/-buildconf/-L. Complete outputs: evidence/b5_0_1/ffmpeg-version.txt, ffmpeg-buildconf.txt, ffmpeg-L.txt, ffprobe-version.txt, ffprobe-buildconf.txt, ffprobe-L.txt.

Actual path: dist/MediaDownloader/bin. Matching copies: bin, dist/MediaDownloader-Portable/bin and .tools/b43/native-build/prefix/bin. FFmpeg and FFprobe both report the exact r2 version.

## Binary SHA256

| File | R1 stable-tag pin | R2 freshly verified |
|---|---|---|
| avcodec-62.dll | c0ef153d97aae81b06f0506e6781c9e8b73cef07ef3a7d62714961f81334828b | ed2983fbeed3925b69181692c574dbe386f21ae403dac1ae57ec47f3d2f26937 |
| avfilter-11.dll | c80fb5902dc066b4902d40c1ab9d27260d1af283eff4efcbc7f0796f252a4ca2 | 4abc7e97cd2174900060ddb97583a0adf837c5aa98a94f13da2084ce6a13a341 |
| avformat-62.dll | 7e7fcd2a65ac1837954f634b1deedf0e3078bfc75fbc7dea9852b9b0962879f2 | f2fcecc42add0aaaa00784b530dd69a7b3c1bce5a11905ba53de501b3440ec6c |
| avutil-60.dll | c6719d09dd28d3e4044d2adb86800ad011ecd5d1471f065cbe68a9295590a22e | 934fd0afb66382b2eda11ca6f5d09bdad8f27a05096d9ab22914653f7328f1b6 |
| ffmpeg.exe | 527e83b2893b38d698ac0acbb59a5e47dfc4cca1f636b2264fe89488f2c59a8b | 6f7016342cc4a9bd965fe0efbd254b7dd2ac8eb62e02fbf349952000196ea521 |
| ffprobe.exe | 59708acc8a9a60cf9bc652e66f79a1a0bc216f57213be647ac78a87d7d02db19 | a6376f09b16d79b76ca84daf5bb1a9d2c1d2cf8261070c7891984620542c33ad |
| swresample-6.dll | 868b7b475dd2d06682cb1c565cc6fdcd2a75958adf30fd4bcb1c8acb28794770 | 9e1afc7e0295b59d9959470e1641fc6663764b48ee4f3ad17b4102720d90b1f4 |
| swscale-9.dll | 82e93e16ca85860fe782fc5a226c601435db2d7083c3e3cc1bc14dd3ccd57690 | 564156a06f91ba06d9fb2947437fb0b4127d1686e90c48e9d78e04627121b1bc |

## Corresponding build/distribution materials

All nine source archives in dist/MediaDownloader/SOURCES match build/native-runtime-lock.json; upstream FFmpeg revision is confirmed in receipt.json. Exact bundled recipe matches b9794ef, with SHA256 8fd7bbbe750429049c4ad3f65179ba796a1022bea670e7f714cde60b5ead49ac. Generated config.h/config_components.h/config.mak/config.log, ffversion.h, full command history and receipt accompany the binaries. .tools/b43/chapter-fix-build.log records configure/build/install.

native-relink-materials.zip SHA256: 39d3eb5f99ae0a9375a1801637be6b24210db558c445eef4000e5fca86de70cd. ZIP integrity passes; 709 FFmpeg objects, including libavformat/ffmetadec.o, match local compiled objects byte-for-byte. Supplied static archives and toolchain archives also match their local build inputs. Build instructions, source patch declaration and component license grants are present. Bundle inventory hashes for every runtime/source entry match actual files.

Reason r2 exists: real chapter embedding failure recorded by b9794ef and docs/RC1_CHAPTER_METADATA_FIX.md on the repair branch. This reconciliation additionally runs the real FFmpegMetadataPP chapter test using Chinese titles and a path with spaces; it passes. This is a functional demuxer correction, not a packaging-only change, so full 8K download/merge/probe/decode was required and performed.

No new external dependency or license mode was enabled. This is technical source/build/license correspondence evidence, not public-distribution legal approval. Public Distribution Gate remains NEEDS LEGAL REVIEW.
