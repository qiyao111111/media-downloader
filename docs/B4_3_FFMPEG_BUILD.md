# B4.3 MediaDownloader FFmpeg runtime build

Old BtbN n8.1.3-14-g330caae0c1-20261001 is removed from the release payload.
The new own-source build is FFmpeg 8.1.3-g330caae0c1-md-b43-r1, exact official
revision 330caae0c1acccd2222edc52a05940c574561ce5. Source archive SHA256
485bfaa6cdce46ba8e61b2866133d7118fc07f65d790a6295c31e6f0e2a62e71.

Actual full binary outputs:
[version](evidence/b4_3-ffmpeg-version.txt),
[buildconf](evidence/b4_3-ffmpeg-buildconf.txt),
[license](evidence/b4_3-ffmpeg-license.txt),
[native import paths](evidence/b4_3-native-imports.json).
Actual -L reports LGPL version 2.1 or later. Configuration explicitly uses
--disable-gpl --disable-nonfree --disable-version3, --enable-shared,
--disable-static, --disable-autodetect and --disable-everything, then enables
only the application's required formats/codecs/filters. Network, ffplay and
avdevice are disabled; yt-dlp downloads streams, FFmpeg reads local streams.
This is a fact about the built configuration, not a legal opinion about the
whole application or its separately incorporated code.

| Static dependency | Exact version/revision | Purpose | Original grant |
|---|---|---|---|
| dav1d | 1.5.4 / 54706fc6bc0cdecab7e9593974a4039cc038fca7 | AV1 full decode | BSD-2-Clause + assembly notices |
| Opus | 1.6.1 / 22244de5a79bd1d6d623c32e72bf1954b56235be | existing Opus output | BSD-3-Clause + patent references |
| LAME | 3.100 | existing MP3 output | LGPL-2.0-or-later |
| zlib | 1.3.1 / 51b7f2abdade71cd9bb0e7a373ef2610ec6f9daf | PNG conversion | Zlib |
| OpenH264 | 2.6.0 / 652bdb7719f30b52b08e506645a7322ff1b2cc6f | existing explicit H264 conversion | BSD-2-Clause |
| libvpx | 1.15.2 / d168454ecd099805c675d4a98c66f4891373302a | explicit VP9 conversion | BSD-3-Clause + PATENTS/ISC assembly |
| libwebp / SharpYUV | 1.6.0 / 4fa21912338357f89e4fd51cf2368325b59e9bd9 | existing WebP thumbnail conversion | BSD-3-Clause + PATENTS |

Seven external source trees plus FFmpeg and QuickJS have verified archives.
Source versions/revisions/URLs/digests are in [native lock](../build/native-runtime-lock.json).
OpenH264 is built from source, not Cisco's binary; no Cisco binary patent
coverage is claimed. LibYUV is not linked into libvpx: actual .a members were
inspected; its configure helper switch alone is not distribution evidence.
No Chromaprint, FFTW, GPL encoder, external Cairo/GLib/Pango or Deno is linked.
The old AVI recode choice's missing libxvid was already unavailable in the
old LGPL build; no GPL encoder is added to conceal that prior limitation.
Default highest quality remains stream-copy merge/mux, never upscale,
FPS reduction, video re-encode or HDR-to-SDR conversion. Selector code is unchanged.

Compiler: LLVM-MinGW 20260922 UCRT, Clang 23.1.2,
LLVM85ac560262434c9ccfc0c183ec22d4138ed647fb, MinGW-w64
57b595039040eaa15bece85b7cc71d952281b269. Development-only CMake4.4.3,
Meson1.12.1, Ninja1.13.2; MSYS make4.4.1-3, nasm3.02-1, pkgconf3.0.7-1,
diffutils3.12-1, perl5.42.3-2. No build tools are required on the target PC.
Child-only build PATH; no global environment/security modifications.

[Build script](../build_native_runtime.py) and
[recipient instructions](../redistribution/NATIVE_BUILD_INSTRUCTIONS.txt)
are shipped in SOURCES with all exact archives, configure argv, config.h,
config_components.h, config.mak/config.log, ffversion.h, commands/receipt.
No local source patches; upstream zlib CMake generates/renames config headers.
Version metadata is supplied by configure/CMake, not a source-code patch.
For Chinese development paths, MSYS pkgconf uses Windows 8.3 ASCII short
prefixes. If unavailable, build in an ASCII checkout. Product Chinese/space
download paths remain supported.

Six separately replaceable FFmpeg DLLs and ffmpeg.exe/ffprobe.exe are in bin.
Statically incorporated C++/unwind/Winpthreads runtime has its original LLVM,
MinGW-w64 and Winpthreads notices. PE imports contain no external Winpthread
or C++ DLL: linkage is static; Windows API-set/UCRT imports are OS-provided.
SOURCES/native-relink-materials.zip supplies rebuilt static dependency archives,
compiled FFmpeg objects and actual compiler runtime .a files. Source/relink
provision is direct, not an invented future written offer. LGPL LAME source,
linkable materials, notices and replacement instructions accompany the DLL.
The IJG required credit and original headers are retained separately.

Preserved build/test failures: a candidate inherited the enclosing project
Git version; GIT_CEILING_DIRECTORIES and explicit version metadata corrected it.
A candidate required libwinpthread-1.dll; static pkg-config flags plus forced
relink removed the dependency. The first shrink configuration missed the WebP
muxer and mjpeg2jpeg thumbnail filter; runnable real conversion checks caught
it and the build configuration was corrected. Final evidence refers to the
corrected binaries, not these failed candidates.
The first frozen diagnostics run also exposed default Windows text decoding
of the UTF-8 Chinese configure path. Explicit UTF-8 diagnostics fixed that
runtime-only issue; no media operation/selector behavior was changed.

Full real 1080P/4K/8K, VP9/WebM, H264/MP4, AV1+Opus/MKV, six audio modes,
ffprobe and full decode evidence are linked in the release gate report.
[FFmpeg primary redistribution reference](https://ffmpeg.org/legal.html).
