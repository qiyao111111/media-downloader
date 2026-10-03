# B4.2 actual distribution inventory

2026-10-02 · internal RC 0.9.0rc1 · `codex/b4-2-final-release-gate`.

**File inventory complete; target-specific transitive license/source inventory remains open.**
1301 实际 bundle files、80 EXE/DLL/PYD、1347 embedded PYZ modules、147 LICENSES files。
ZIP 与实际安装 Setup payload 对这 1301 个文件逐文件 SHA256 相同；Portable 另有 `portable.flag`，
安装器另外生成 `unins000.exe/unins000.dat`。不是仅扫描 requirements，也没有把已安装但未发行的包混入。

逐文件 exact path、bytes、SHA、component ownership、origin、PE version：
[distribution-files.json](evidence/b4_2-distribution-files.json)。其 embedded_modules 列表列出全部实际 PYZ members。
69 个 PyInstaller-collected native files 的 exact build inputs/digest 见
[native origins](evidence/b4_2-native-origins.json)；另外 11 个 bin 文件来自 pinned FFmpeg/Deno archives。
实际 version resource 重新读取，见 [native versions](evidence/b4_2-native-version-resources.json)。
transitive_binary_SBOM_complete=false；没有伪造全量 `SBOM.spdx.json`。

## Component/license/source matrix

文件名称相对 actual bundle root。`PYZ` 表示 MediaDownloader.exe 内嵌 Python archive，不是系统 executable。
源 grant 位于 licenses/source-notices 或完整 source archive，来源/固定 hash 位于 source-provenance.json。
PASS 仅指该行明确列出的义务，不代表整个 release PASS。状态只用 PASS / NOT APPLICABLE /
NEEDS LEGAL REVIEW / BLOCKED。

| Component | Version | Exact distributed files | Origin | License | Source location | Required notices | Required source/relink materials | Status |
|---|---|---|---|---|---|---|---|---|
| Original Plutoeat/yt-dlp-gui + application | base 6abfce5; RC0.9.0rc1 | MediaDownloader.exe!PYZ/app,core,gui,models,services,configs; LICENSE text | project MIT source | MIT | repository/base + current packaging changes | Gaius Pluto original copyright/grant/disclaimer retained | none under MIT | PASS |
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
| liblzma | 5.2.5 CPython PCbuild pin; no independent binary version claim | _internal/_lzma.pyd | build Python | incorporated XZ terms | exact Python LICENSE/source notices | retained incorporated grant | target source/compiled subset review | NEEDS LEGAL REVIEW |
| libffi | PCbuild3.4.4 pin; PE version absent | _internal/libffi-8.dll | exact Python installation file | MIT | Python LICENSE | original copyright/grant | binary correspondence/notice completeness under supplier review | NEEDS LEGAL REVIEW |
| libmpdec | 4.0.0, runtime query | _internal/_decimal.pyd | build Python | BSD-2-Clause | Modules/_decimal/libmpdec/LICENSE.txt | original copyright/grant | none | PASS |
| HACL* / CPython incorporated helpers | exact Python3.13.13 source; compiled subset not separately proven | incorporated Python DLL/PYD | build Python | component-specific original grants | exact Modules/_hacl source/texts | retained original incorporated notices | target-subset notice/source correspondence review | NEEDS LEGAL REVIEW |
| PySide6 / Shiboken | 6.11.2 | QtCore/Gui/Network/Widgets.pyd, pyside6.abi3.dll, Shiboken.pyd,shiboken6.abi3.dll; PYZ | exact installed Qt-for-Python wheels | selected LGPL-3.0-compatible route + third-party terms | pyside-setup6.11.2 exact source and grants | full LGPL3/GPL3 and selected source attribution texts | sources provided; onedir replacement path documented; LGPL §4 applicability/correspondence review | NEEDS LEGAL REVIEW |
| QtBase | 6.11.2 | Qt6Core/Gui/Network/Widgets/OpenGL.dll + relevant plugins below | exact PySide6 wheel | selected LGPL-3.0-compatible route + incorporated grants | QtBase6.11.2 exact source | selected Windows-module notices retained | shared-library replacement/source/build correspondence review | NEEDS LEGAL REVIEW |
| QtSvg | 6.11.2 | Qt6Svg.dll; qsvg.dll,qsvgicon.dll | exact PySide6_Addons wheel | LGPL-3.0-compatible route + incorporated grants | QtSvg6.11.2 exact source | full applicable texts/attribution | shared DLL replacement/source correspondence review | NEEDS LEGAL REVIEW |
| QtImageFormats | 6.11.2 | qicns/qtga/qtiff/qwbmp/qwebp.dll | exact PySide6_Addons wheel | LGPL-3.0-compatible route + incorporated grants | QtImageFormats6.11.2 exact source | applicable grants preserved | target static inclusion/source correspondence review | NEEDS LEGAL REVIEW |
| Qt selected third-party source candidates | versions recorded individually in Qt-source-attributions.json | candidate incorporated code in modules/plugins above; not every source candidate asserted compiled | exact Qt/PySide source metadata | each original metadata License field; no generic LGPL reassignment | 41 selected attribution files + referenced full texts + source archives | metadata-directed copyright/license originals retained | final wheel's target-specific static mapping/terms review | NEEDS LEGAL REVIEW |
| Microsoft VC runtime | root14.42.34438.0; wheel14.44.35211.0 | actual VCRUNTIME/MSVCP files below | Python/PySide6/Shiboken build inputs, SHA identical | actual Microsoft/Python Windows redist conditions | Python-LICENSE Additional Conditions; unchanged original DLLs | original DLLs/copyright retained; downstream terms review | no speculative entitlement/source obligation asserted | NEEDS LEGAL REVIEW |
| FFmpeg / FFprobe / ffplay | n8.1.3-14-g330caae0c1-20261001 | bin/ffmpeg.exe,ffprobe.exe,ffplay.exe + seven av*/sw* DLLs | pinned BtbN archive; 10 files CI SHA identical | own -L LGPL3+; external GPL/LGPL obligations separately open | exact FFmpeg330caae + BtbNe88e49f recipes | own grants/configuration retained; full static dependency notices incomplete | complete corresponding external/transitive/generated sources not delivered | BLOCKED |
| Chromaprint | aed8eba exact source pin | statically linked via avformat target; CI -DFFT_LIB=fftw3 | matching BtbN target recipe/logs | MIT + LGPL2.1 + chosen FFT terms | exact source snapshot and original LICENSE.md | Lukas Lalinsky grant/full LGPL2.1 supplied | matching provider build/modification/source closure remains in FFmpeg gate | BLOCKED |
| FFTW3 | 93ed4c7 exact source pin | same target's -lfftw3 static linkage | matching CI + recipe25-fftw3.sh | GPL-2.0-or-later, actual COPYRIGHT | exact snapshot; COPYING/COPYRIGHT | Matteo Frigo/MIT notices/full GPL2 supplied | combined-binary GPL/LGPL route review; generated/provider-modified source correspondence open | BLOCKED |
| Other FFmpeg static/transitive libraries | actual enabled flags + 128 observed -l items; no fabricated exact version | incorporated into seven FFmpeg DLLs/three EXEs; Windows imports distinguished | actual buildconf + matching target CI/recipes | per actual linked source; complete mapping NOT ESTABLISHED | fixed recipes; candidate download-cache not inventoried/provided as CS | exact complete target notice set not delivered | complete resolved inputs, generated sources, patches/toolchain materials required as applicable | BLOCKED |
| Deno | 2.9.7 | bin/runtime/deno.exe | exact pinned release archive | direct MIT + separate incorporated terms | direct LICENSE, exact Cargo.lock | Deno direct grant retained; transitive set incomplete | full target-specific notice/source mapping still open | BLOCKED |
| TypeScript | 6.0.3, Deno self-report | embedded Deno compiler JS | Deno exact source include00_typescript.js | Apache-2.0 | pinned TS6.0.3 LICENSE + compiler copyright header | actual Microsoft notice/full grant retained | no direct Apache source duty | PASS |
| Node / Undici type declarations | exact Deno v2.9.7 source pin | embedded Deno compiler declarations | Deno source embedding macro | MIT | two pinned source LICENSE files | original MIT grants/copyright retained | none under direct grants | PASS |
| V8 / ICU / Rust Deno dependencies | V8 15.0.245.2-rusty self-report; remaining target mapping open | incorporated deno.exe | actual Deno executable; Cargo.lock includes nonruntime records | each actual target grant; full binary match not established | candidate exact release sources/Cargo.lock | full target-specific notices incomplete | source/relink requirements must follow actual included grants | BLOCKED |
| PyInstaller bootloader/loader | 6.22.3 | MediaDownloader.exe + loader PYZ/members | installed PyInstaller bootloader | GPL2+ with original distribution exception | installed COPYING.txt | original exception/text retained | no invented application GPL duty from bootloader exception; loader unchanged | PASS |
| PyInstaller runtime hooks/helpers | 6.22.3 | pyi_rth_* / _pyi_rth_utils embedded code | exact runtime hook sources | Apache-2.0 | 8 retained original hook/helper files | copyright headers/full Apache retained | no direct source duty; no modifications | PASS |
| Inno Setup generated engine | 6.7.3 build tool; generated EXE resource records app version | Setup executable bootstrap; unins000.exe/unins000.dat | pinned Inno compiler package, generated unmodified engine | exact Inno package grant | Inno-Setup-LICENSE.txt | complete original binary notice/web-address retention scope review | no compiler payload/source duty claimed | NEEDS LEGAL REVIEW |
| Mesa/LLVM Qt software renderer | prior wheel exact-file proof | opengl32sw.dll absent from final ZIP/Setup | optional wheel file removed from collection | not assigned to final runtime | renderer-exclusion evidence | no standalone renderer notice required for this absent file | no final renderer source obligation; opaque FFmpeg/Deno LLVM scope stays open | NOT APPLICABLE |
| GPL-only unused Qt modules / compiled translations | absent | no QtPdf/VirtualKeyboard/QML/Quick payload; no .qm | absent final file/module inventory | no runtime grant assignment | actual inventory | complete provided source snapshots retain their own original source licenses | no runtime relink duty for absent binaries | NOT APPLICABLE |
| PyInstaller analysis/build integrations and build-only Python tools | absent final PYZ | no PyInstaller analysis package, yt_dlp.__pyinstaller, setuptools,packaging,altgraph,pefile,win32ctypes | build host only | no runtime grant assignment | actual embedded_modules evidence | not listed as redistributed runtime components | no runtime source obligation | NOT APPLICABLE |

## Inventory limits and materials actually shipped

All actual paths/hashes are inventoried; opaque static dependency completeness is explicitly **BLOCKED**, not hidden behind a synthetic SBOM.
Each source archive retains its own original license-bearing source files, including uncompiled examples/platform code.
Source distribution is not described as distributing those components as executable modules.
LICENSES contains 147 selected documents/data/source files, including 16 SHA-verified provenance entries (9 source archives,
7 direct text/Cargo records), full required grants obtained so far, and actual runtime-hook copyright files.
Unknown-to-this-audit transitive correspondence is not falsely assigned a passing license.
See [license closure](B4_2_LICENSE_CLOSURE.md) for exact blocked work and professional review clauses.

## Exact native file list (version resources, not inferred versions)

The table below is generated from the actual final payload. Missing PE version fields mean the file does not self-report a version;
the component's independently evidenced version appears in the matrix above.

| Exact file | PE FileVersion | Component |
|---|---|---|
| `_internal/_asyncio.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_bz2.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_ctypes.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_decimal.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_elementtree.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_hashlib.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_lzma.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_multiprocessing.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_overlapped.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_queue.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_socket.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_sqlite3.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_ssl.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_uuid.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/_wmi.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/libcrypto-3.dll` | 3.0.19 | OpenSSL |
| `_internal/libffi-8.dll` | not self-reported | libffi |
| `_internal/libssl-3.dll` | 3.0.19 | OpenSSL |
| `_internal/pyexpat.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/PySide6/MSVCP140.dll` | 14.44.35211.0 | Microsoft VC runtime |
| `_internal/PySide6/MSVCP140_1.dll` | 14.44.35211.0 | Microsoft VC runtime |
| `_internal/PySide6/MSVCP140_2.dll` | 14.44.35211.0 | Microsoft VC runtime |
| `_internal/PySide6/plugins/generic/qtuiotouchplugin.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/iconengines/qsvgicon.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/imageformats/qgif.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/imageformats/qicns.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/imageformats/qico.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/imageformats/qjpeg.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/imageformats/qsvg.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/imageformats/qtga.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/imageformats/qtiff.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/imageformats/qwbmp.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/imageformats/qwebp.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/networkinformation/qnetworklistmanager.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/platforms/qdirect2d.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/platforms/qminimal.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/platforms/qoffscreen.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/platforms/qwindows.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/styles/qmodernwindowsstyle.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/tls/qcertonlybackend.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/tls/qopensslbackend.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/plugins/tls/qschannelbackend.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/pyside6.abi3.dll` | not self-reported | Qt / PySide6 / Shiboken |
| `_internal/PySide6/Qt6Core.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/Qt6Gui.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/Qt6Network.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/Qt6OpenGL.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/Qt6Svg.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/Qt6Widgets.dll` | 6.11.2.0 | Qt / PySide6 / Shiboken |
| `_internal/PySide6/QtCore.pyd` | not self-reported | Qt / PySide6 / Shiboken |
| `_internal/PySide6/QtGui.pyd` | not self-reported | Qt / PySide6 / Shiboken |
| `_internal/PySide6/QtNetwork.pyd` | not self-reported | Qt / PySide6 / Shiboken |
| `_internal/PySide6/QtWidgets.pyd` | not self-reported | Qt / PySide6 / Shiboken |
| `_internal/PySide6/VCRUNTIME140.dll` | 14.44.35211.0 | Microsoft VC runtime |
| `_internal/PySide6/VCRUNTIME140_1.dll` | 14.44.35211.0 | Microsoft VC runtime |
| `_internal/python3.dll` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/python313.dll` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/select.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/shiboken6/MSVCP140.dll` | 14.44.35211.0 | Microsoft VC runtime |
| `_internal/shiboken6/Shiboken.pyd` | not self-reported | Qt / PySide6 / Shiboken |
| `_internal/shiboken6/shiboken6.abi3.dll` | not self-reported | Qt / PySide6 / Shiboken |
| `_internal/shiboken6/VCRUNTIME140.dll` | 14.44.35211.0 | Microsoft VC runtime |
| `_internal/shiboken6/VCRUNTIME140_1.dll` | 14.44.35211.0 | Microsoft VC runtime |
| `_internal/sqlite3.dll` | 3.50.4.0 | SQLite |
| `_internal/unicodedata.pyd` | 3.13.13 | Python runtime / stdlib / PyInstaller runtime data |
| `_internal/VCRUNTIME140.dll` | 14.42.34438.0 | Microsoft VC runtime |
| `_internal/VCRUNTIME140_1.dll` | 14.42.34438.0 | Microsoft VC runtime |
| `_internal/yaml/_yaml.cp313-win_amd64.pyd` | not self-reported | PyYAML / LibYAML |
| `bin/avcodec-62.dll` | 62.28.103 | FFmpeg / FFprobe / ffplay |
| `bin/avdevice-62.dll` | 62.3.103 | FFmpeg / FFprobe / ffplay |
| `bin/avfilter-11.dll` | 11.14.103 | FFmpeg / FFprobe / ffplay |
| `bin/avformat-62.dll` | 62.12.103 | FFmpeg / FFprobe / ffplay |
| `bin/avutil-60.dll` | 60.26.103 | FFmpeg / FFprobe / ffplay |
| `bin/ffmpeg.exe` | not self-reported | FFmpeg / FFprobe / ffplay |
| `bin/ffplay.exe` | not self-reported | FFmpeg / FFprobe / ffplay |
| `bin/ffprobe.exe` | not self-reported | FFmpeg / FFprobe / ffplay |
| `bin/runtime/deno.exe` | 2.9.7 | Deno |
| `bin/swresample-6.dll` | 6.3.103 | FFmpeg / FFprobe / ffplay |
| `bin/swscale-9.dll` | 9.5.103 | FFmpeg / FFprobe / ffplay |
| `MediaDownloader.exe` | 0.9.0rc1 | application + embedded Python packages + PyInstaller bootloader |
