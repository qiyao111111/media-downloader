# B4.3 actual distribution inventory

Windows x64 internal RC 0.9.0rc1. File-level inventory uses the final onedir
payload, followed by actual Portable ZIP / installed Setup payload SHA checks.
[Every exact file, bytes, SHA256, owner/origin and retained native version](evidence/b4_3-distribution-files.json).
Embedded PYZ modules are inventoried independently; installed developer packages
are not treated as redistributed merely because they exist on the build host.

| Measure | B4.2 | B4.3 |
|---|---:|---:|
| Actual payload files | 1301 | 1334 |
| EXE / DLL / PYD | 80 | 78 |
| licenses directory files | 147 | 160 |
| Expanded payload bytes | 488778232 | 312590344 |

Final native bin is 18647040 bytes, 8 FFmpeg files plus qjs.exe.
File/license count rises because exact sources/relink materials and compiler
notices now accompany the own build. Expanded payload falls by
176187888 bytes. The target is traceability,
not hiding source materials to force a smaller license count.
[Comparison and unchanged native-origin identity](evidence/b4_3-distribution-comparison.json).

Direct native build/source/grant matrix below uses only PASS / NOT APPLICABLE /
NEEDS LEGAL REVIEW / BLOCKED. PASS is scoped to the row's stated retained
materials and obligations, not a legal opinion that all public distribution
terms are cleared. Qt/Microsoft final terms still require professional review.

| Component | Version | Exact distributed files | Origin | License | Source location | Required notices | Required source/relink materials | Status |
|---|---|---|---|---|---|---|---|---|
| Original Plutoeat/yt-dlp-gui + application | base b8b18a9; RC0.9.0rc1 | MediaDownloader.exe!PYZ/app,core,gui,models,services,configs; LICENSE text | project MIT source | MIT | repository/base + current packaging changes | Gaius Pluto original copyright/grant/disclaimer retained | none under MIT | PASS |
| yt-dlp | 2026.8.19 | PYZ/yt_dlp and _internal/yt_dlp/** | exact installed wheel | Unlicense | installed LICENSE, upstream release | actual text retained | none under direct grant | PASS |
| EJS | 0.8.0 | PYZ/yt_dlp_ejs; _internal/yt_dlp_ejs/yt/solver/** | exact installed wheel | Unlicense + solver notices | wheel LICENSE and actual solver header | separate EJS and solver notices retained | none under direct grants | PASS |
| Meriyah | 6.1.4 | _internal/yt_dlp_ejs/yt/solver/lib.min.js | actual solver header | ISC | same JS header | original KFlash notice/grant/disclaimer | none | PASS |
| Astring | 1.9.0 | same lib.min.js | actual solver header | MIT | same JS header | David Bonnet notice/grant/disclaimer | none | PASS |
| PyYAML | 6.0.3 | PYZ/yaml; _internal/yaml/_yaml.cp313-win_amd64.pyd | exact installed wheel | MIT | wheel license | original Ingy/Kirill notice | none | PASS |
| LibYAML | 0.2.5, actual native query | same _yaml.pyd | PyYAML native extension | MIT | exact libyaml0.2.5 License | newly retained exact upstream copyright/license | none | PASS |
| Python | 3.13.13 | _internal/python313.dll,python3.dll,base_library.zip; stdlib PYZ/PYD below | exact build interpreter | PSF + historical/incorporated grants | Python-LICENSE.txt, exact Python source archive | full direct/incorporated notices retained; no interpreter changes claimed | no blanket PSF corresponding-source obligation; MS handled separately | PASS |
| OpenSSL | 3.0.19 | _internal/libcrypto-3.dll,libssl-3.dll | build Python DLLs | Apache-2.0 | pinned LICENSE/ACKNOWLEDGEMENTS | full Apache + exact upstream acknowledgements | no source duty under direct grant; changes none | PASS |
| SQLite | 3.50.4 | _internal/sqlite3.dll, _sqlite3.pyd | build Python | public domain | Python source acknowledgements/declaration | retained declaration | none | PASS |
| Expat | 2.7.5 | _internal/pyexpat.pyd | build Python | MIT | exact Python Modules/expat/COPYING | original notice/grant | none | PASS |
| zlib | 1.3.1, runtime query | incorporated Python runtime | build Python | Zlib | Python Doc/license.rst | original notice/no false origin | modified-source marking if applicable; no changes made | PASS |
| libbzip2 | 1.0.8, CPython PCbuild pin | _internal/_bz2.pyd | build Python | bzip2 | Python incorporated notices | original notice/disclaimer | no direct source duty | PASS |
| liblzma | 5.2.5 CPython PCbuild pin; no independent binary version claim | _internal/_lzma.pyd | build Python | incorporated XZ terms | exact Python LICENSE/source notices | retained incorporated grant | unchanged supplier runtime; retained Python incorporated terms | PASS |
| libffi | PCbuild3.4.4 pin; PE version absent | _internal/libffi-8.dll | exact Python installation file | MIT | Python LICENSE | original copyright/grant | exact supplier input SHA retained; incorporated notices supplied | PASS |
| libmpdec | 4.0.0, runtime query | _internal/_decimal.pyd | build Python | BSD-2-Clause | Modules/_decimal/libmpdec/LICENSE.txt | original copyright/grant | none | PASS |
| HACL* / CPython incorporated helpers | exact Python3.13.13 source; compiled subset not separately proven | incorporated Python DLL/PYD | build Python | component-specific original grants | exact Modules/_hacl source/texts | retained original incorporated notices | unchanged CPython runtime; no new concrete missing text identified | PASS |
| PySide6 / Shiboken | 6.11.2 | QtCore/Gui/Network/Widgets.pyd, pyside6.abi3.dll, Shiboken.pyd,shiboken6.abi3.dll; PYZ | exact installed Qt-for-Python wheels | selected LGPL-3.0-compatible route + third-party terms | pyside-setup6.11.2 exact source and grants | full LGPL3/GPL3 and selected source attribution texts | sources provided; onedir replacement path documented; LGPL §4 applicability/correspondence review | NEEDS LEGAL REVIEW |
| QtBase | 6.11.2 | Qt6Core/Gui/Network/Widgets/OpenGL.dll + relevant plugins below | exact PySide6 wheel | selected LGPL-3.0-compatible route + incorporated grants | QtBase6.11.2 exact source | selected Windows-module notices retained | shared-library replacement/source/build correspondence review | NEEDS LEGAL REVIEW |
| QtSvg | 6.11.2 | Qt6Svg.dll; qsvg.dll,qsvgicon.dll | exact PySide6_Addons wheel | LGPL-3.0-compatible route + incorporated grants | QtSvg6.11.2 exact source | full applicable texts/attribution | shared DLL replacement/source correspondence review | NEEDS LEGAL REVIEW |
| QtImageFormats | 6.11.2 | qicns/qtga/qtiff/qwbmp/qwebp.dll | exact PySide6_Addons wheel | LGPL-3.0-compatible route + incorporated grants | QtImageFormats6.11.2 exact source | applicable grants preserved | target static inclusion/source correspondence review | NEEDS LEGAL REVIEW |
| Qt selected third-party source candidates | versions recorded individually in Qt-source-attributions.json | candidate incorporated code in modules/plugins above; not every source candidate asserted compiled | exact Qt/PySide source metadata | each original metadata License field; no generic LGPL reassignment | 41 selected attribution files + referenced full texts + source archives | metadata-directed copyright/license originals retained | final wheel's target-specific static mapping/terms review | NEEDS LEGAL REVIEW |
| Microsoft VC runtime | root14.42.34438.0; wheel14.44.35211.0 | actual VCRUNTIME/MSVCP files below | Python/PySide6/Shiboken build inputs, SHA identical | actual Microsoft/Python Windows redist conditions | Python-LICENSE Additional Conditions; unchanged original DLLs | original DLLs/copyright retained; downstream terms review | no speculative entitlement/source obligation asserted | NEEDS LEGAL REVIEW |
| PyInstaller bootloader/loader | 6.22.3 | MediaDownloader.exe + loader PYZ/members | installed PyInstaller bootloader | GPL2+ with original distribution exception | installed COPYING.txt | original exception/text retained | no invented application GPL duty from bootloader exception; loader unchanged | PASS |
| PyInstaller runtime hooks/helpers | 6.22.3 | pyi_rth_* / _pyi_rth_utils embedded code | exact runtime hook sources | Apache-2.0 | 8 retained original hook/helper files | copyright headers/full Apache retained | no direct source duty; no modifications | PASS |
| FFmpeg / FFprobe | 8.1.3-g330caae0c1-md-b43-r1 | bin/ffmpeg.exe,ffprobe.exe + six FFmpeg DLLs | own official source build | actual LGPL-2.1-or-later + incorporated grants | SOURCES/FFmpeg-330caae0c1acccd2222edc52a05940c574561ce5.tar.gz | full LGPL2.1, copyright, IJG and assembly credits | source/config/commands/objects/static archives + replaceable DLLs supplied | PASS |
| dav1d | 1.5.4 / 54706fc | static bin/avcodec-62.dll | own official source build | BSD-2-Clause + ISC assembly | SOURCES/dav1d.tar.gz | original COPYING and x86inc notice | direct exact source supplied; no mandatory source offer under BSD | PASS |
| Opus | 1.6.1 / 22244de | static bin/avcodec-62.dll | own official source build | BSD-3-Clause | SOURCES/opus.tar.gz | original COPYING/patent references | direct source supplied | PASS |
| LAME | 3.100 | static bin/avcodec-62.dll MP3 encoder | own official source build; frontend/decoder off | LGPL-2.0-or-later | SOURCES/lame-3.100.tar.gz | COPYING/LICENSE/README/source headers + original website credit | exact source, static archive, FFmpeg objects and relink instructions | PASS |
| native zlib | 1.3.1 / 51b7f2a | static bin/avcodec-62.dll PNG support | own official source build | Zlib | SOURCES/zlib.tar.gz | README and zlib.h notice | direct source; no local source-code patch | PASS |
| OpenH264 | 2.6.0 / 652bdb7 | static bin/avcodec-62.dll explicit encoder | own source build, not Cisco binary | BSD-2-Clause | SOURCES/openh264-2.6.0.tar.gz | original LICENSE | direct exact source/archive supplied; no Cisco binary patent claim | PASS |
| libvpx | 1.15.2 / d168454 | static bin/avcodec-62.dll VP9 encoder | own official source build | BSD-3-Clause + ISC assembly | SOURCES/vpx-1.15.2.tar.gz | LICENSE/PATENTS/AUTHORS/x86inc original notices | direct exact source; LibYUV not linked | PASS |
| libwebp / SharpYUV | 1.6.0 / 4fa2191 | static bin/avcodec-62.dll WebP conversion | own official source build | BSD-3-Clause | SOURCES/webp-1.6.0.tar.gz | COPYING/PATENTS/AUTHORS | direct exact source | PASS |
| QuickJS-NG | 0.17.0 / 6d46d07 | bin/runtime/qjs.exe | own official source build; mimalloc off | MIT | SOURCES/quickjs-ng-0.17.0.tar.gz | original LICENSE + compiled source notices | direct source, pinned build recipe; no MIT source-offer duty | PASS |
| LLVM compiler runtime / libc++ / libc++abi / unwind | Clang23.1.2 / LLVM85ac560 | static native FFmpeg and QuickJS files; C++/unwind in avcodec | exact LLVM-MinGW20260922 compiler/runtime | Apache-2.0 WITH LLVM-exception + original historical grants | pinned upstream revision/toolchain origin in SOURCES lock | full original LLVM-runtime-LICENSE.txt and Apache text | compiler runtime .a inputs for relink retained; compiler executable not shipped | PASS |
| MinGW-w64 / Winpthreads runtime | release20260922 / MinGW57b5950 | native startup/CRT and static pthread portions | exact own compiler runtime | original permissive MIT/BSD/public-domain subsets | pinned toolchain origin/revision | full MinGW runtime and Winpthreads notices | actual pthread archive supplied; no libwinpthread-1.dll distribution | PASS |

No Deno executable or Deno-only V8/Rust/ICU/TypeScript/Node declarations are
redistributed. No old BtbN binary, ffplay, Chromaprint, FFTW, Cairo/GLib/Pango
runtime, optional Mesa software renderer, mimalloc, LibYUV or build-only
compiler/MSYS/CMake/Meson/Ninja/Inno compiler is redistributed. These removed
or build-only components are NOT APPLICABLE as bundled runtimes. Sources may
contain unbuilt upstream tests/examples/other-platform code; no assertion that
such source-only components are compiled into the application is made.

PyInstaller onedir: Qt DLL/PYD/plugins remain physical, separately replaceable
files; no private signature/key enforcement embeds them irrevocably in the EXE.
Actual Qt DLLs:

- `_internal/PySide6/Qt6Core.dll`
- `_internal/PySide6/Qt6Gui.dll`
- `_internal/PySide6/Qt6Network.dll`
- `_internal/PySide6/Qt6OpenGL.dll`
- `_internal/PySide6/Qt6Svg.dll`
- `_internal/PySide6/Qt6Widgets.dll`

Actual plugin DLLs:

- `_internal/PySide6/plugins/generic/qtuiotouchplugin.dll`
- `_internal/PySide6/plugins/iconengines/qsvgicon.dll`
- `_internal/PySide6/plugins/imageformats/qgif.dll`
- `_internal/PySide6/plugins/imageformats/qicns.dll`
- `_internal/PySide6/plugins/imageformats/qico.dll`
- `_internal/PySide6/plugins/imageformats/qjpeg.dll`
- `_internal/PySide6/plugins/imageformats/qsvg.dll`
- `_internal/PySide6/plugins/imageformats/qtga.dll`
- `_internal/PySide6/plugins/imageformats/qtiff.dll`
- `_internal/PySide6/plugins/imageformats/qwbmp.dll`
- `_internal/PySide6/plugins/imageformats/qwebp.dll`
- `_internal/PySide6/plugins/networkinformation/qnetworklistmanager.dll`
- `_internal/PySide6/plugins/platforms/qdirect2d.dll`
- `_internal/PySide6/plugins/platforms/qminimal.dll`
- `_internal/PySide6/plugins/platforms/qoffscreen.dll`
- `_internal/PySide6/plugins/platforms/qwindows.dll`
- `_internal/PySide6/plugins/styles/qmodernwindowsstyle.dll`
- `_internal/PySide6/plugins/tls/qcertonlybackend.dll`
- `_internal/PySide6/plugins/tls/qopensslbackend.dll`
- `_internal/PySide6/plugins/tls/qschannelbackend.dll`

No compiled Qt translation .qm files, GPL-only QtPdf/VirtualKeyboard/QML/Quick
modules or opengl32sw.dll are present. Direct app imports remain QtCore, QtGui,
QtWidgets, QtNetwork. QtSvg/QtImageFormats plugins and Qt6OpenGL are actually
shipped and remain in the inventory even if the app does not use GL widgets.
Qt source attributions are module-scoped source candidates; no fabricated full
static target-wheel SBOM is asserted. LGPL library replacement/combined-work
terms remain a professional legal-review item.

Actual Microsoft redistribution files, not mere matching strings:

| File | Supplier | File version |
|---|---|---|
| _internal/PySide6/MSVCP140.dll | PySide6 | 14.44.35211.0 |
| _internal/PySide6/MSVCP140_1.dll | PySide6 | 14.44.35211.0 |
| _internal/PySide6/MSVCP140_2.dll | PySide6 | 14.44.35211.0 |
| _internal/PySide6/VCRUNTIME140.dll | PySide6 | 14.44.35211.0 |
| _internal/PySide6/VCRUNTIME140_1.dll | PySide6 | 14.44.35211.0 |
| _internal/shiboken6/MSVCP140.dll | Shiboken6 | 14.44.35211.0 |
| _internal/shiboken6/VCRUNTIME140.dll | Shiboken6 | 14.44.35211.0 |
| _internal/shiboken6/VCRUNTIME140_1.dll | Shiboken6 | 14.44.35211.0 |
| _internal/VCRUNTIME140.dll | Python | 14.42.34438.0 |
| _internal/VCRUNTIME140_1.dll | Python | 14.42.34438.0 |

Windows KERNEL32/API-MS-UCRT/User32/Bcrypt/etc imported from the OS are not
physically redistributed. PyInstaller collects Python/Qt supplier DLLs as
above; Inno carries only its Setup/uninstaller engine, not extra VC DLL files.
Python 3.13.13 runtime, python313.dll/python3.dll, base_library.zip, native
stdlib dependencies and original PSF/incorporated notices are retained.
Python's own direct grant is not a newly invented product blocker; Microsoft
Distributable Code downstream terms are reviewed separately.

Inno Setup6.7.3 compiler is build-only; generated Setup/uninstaller engine is
redistributed, original grant/copyright/website materials retained. Commercial
use licensing review is a business item separate from the download/runtime
technical gate; see the exact retained grant and
[official Inno site](https://jrsoftware.org/isinfo.php).

Source access uses accompanying source archives/config/relink inputs and
source-offer/README.txt, not a generic GitHub link or invented written offer.
No complete transitive SPDX SBOM is emitted: upstream target-static Qt
attribution correspondence is not fully independently established. Exact
physical inventory and direct native source pins are provided without that
false assertion. Public Distribution Gate remains NEEDS LEGAL REVIEW.
