# B4.3 runtime and distribution simplification

Base b8b18a9acb8fa1ba01f6a51e17bb98b600a6ac0b; branch
codex/b4-3-release-simplification. Historical B4.2 result is unchanged.
This phase changes runtime discovery/diagnostics, native builds, packaging,
redistribution materials, tests and reports. No format-selector algorithm,
download-worker/Manager behavior, UI, platform, branding or B5 changes.

The download runtime remains yt-dlp2026.8.19 + independent yt-dlp-ejs0.8.0.
After real native challenge/metadata/media/cookie/proxy A/B, QuickJS-NG0.17.0
replaces bundled Deno2.9.7. The selected format sets are identical for fixed
8K30 SDR and 8K60 HDR10 sources. Challenge timing is slower in one probe,
without format loss or failure. No solver patch or runtime wrapper library.
Explicit developer overrides remain unsupported for product runtime use;
no automatic JS system PATH/Deno fallback or remote EJS download.

The opaque BtbN FFmpeg is replaced by an own official pinned source build,
with seven minimal traced static dependencies. AV1 full decode, VP9/H264,
Opus/AAC, six current audio formats, MP4/MKV/WebM muxing, probe and thumbnail /
explicit video conversion support are preserved. MP3 uses traced LAME3.100,
not an unexplained bundled encoder. Default video operations remain copy/mux.
Eight FFmpeg native files plus qjs.exe total 18,647,040 bytes.

Native GPL/nonfree/version3 features are explicitly disabled. Chromaprint,
FFTW, ffplay, Deno target Rust/V8/ICU/TypeScript and their component-only
materials are removed from actual RC payload. No blind mass-license collection
or wholesale UI framework replacement. Qt/PySide6, Python and PyInstaller
remain the prior runtimes, with direct source grants and supplier file identity.

SOURCES supplies nine exact archives and native build/relink materials with
the actual configuration and SHA256 pins. LICENSES/THIRD_PARTY_NOTICES match
actual new runtime distribution, including static compiler startup/C++/pthread
notices and IJG/assembly credits. LLVM compiler runtime is physically incorporated
and declared separately from the absent Qt Mesa/LLVM software renderer.

One minimum diagnostics fix explicitly decodes native version output as UTF-8
in runtime_manager.health and ffmpeg_utils.version. The own FFmpeg version
string embeds the Chinese build path; default Windows text decoding failed
in the windowed frozen build. A real health/version check now guards this path.
No ffprobe media-validation or download-selection behavior is changed.

The final portable and installed acceptance runners use fresh Chinese/space
output folders, preventing previously downloaded files from masquerading as
new complete downloads. Real final artifact behavior, unit counts, hashes,
crash/restart and installer removal evidence are in the gate report.

Technical Release Gate, Clean Machine Gate and Public Distribution Gate are
separate. Local Windows-only PATH tests prove frozen runtime routing locally,
not independent clean Windows. No available independent Sandbox/VM/PC;
Clean Machine stays NOT TESTED. The test kit has final ZIP/Setup/checksums,
read-only evidence collector/manual checklist, and a .wsb mapping only the kit.
The .wsb is prepared configuration, not an executed acceptance result.

Qt/PySide LGPL replacement/combined-work terms and Microsoft downstream
Distributable Code conditions still require professional review. Inno commercial
use is a separate release-business question. No formal legal clearance,
commercial entitlement, source service or written-offer issuer is fabricated.
Native materials are provided directly; no Public Distribution PASS inferred
from inventory/source existence alone.

[JS comparison](B4_3_JS_RUNTIME_COMPARISON.md),
[FFmpeg build](B4_3_FFMPEG_BUILD.md),
[distribution inventory](B4_3_DISTRIBUTION_INVENTORY.md),
[release gates](B4_3_RELEASE_GATES.md).
