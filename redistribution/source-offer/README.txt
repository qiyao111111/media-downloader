SOURCE ACCESS AND SHARED-LIBRARY REPLACEMENT — INTERNAL RC

Native source materials are supplied directly in ../SOURCES with this copy:
FFmpeg exact source archive, QuickJS-NG, dav1d, Opus, LAME, zlib, OpenH264,
libvpx and libwebp/SharpYUV exact source archives. Their immutable revisions,
original URLs and SHA256 digests are in native-runtime-lock.json.
BUILD_INSTRUCTIONS.txt and build_native_runtime.py provide actual build
commands, toolchain provenance and the minimal enabled configuration.
config.h/config_components.h/config.mak/config.log/ffversion.h, commands.json
and receipt.json record the actual build; native-relink-materials.zip contains
compiled FFmpeg objects, rebuilt static libraries and compiler runtime archives.
No local source-code patches. No private download location/key is required.

Exact QtBase, QtSvg, QtImageFormats and PySide6 6.11.2 source archives, plus
Python 3.13.13 source, are supplied in ../licenses/source-code. Their original
source grants and applicable third-party acknowledgements are retained under
../licenses/source-notices. ../licenses/source-provenance.json identifies
source/archive digests; ../licenses/Qt-source-attributions.json identifies
selected module attribution references. Package grants, bootloader exception,
runtime hook source headers and EJS embedded solver notices are retained.

Close the application and its workers, back up the original files, and replace
compatible Qt/PySide6 libraries/plugins in _internal/PySide6 and shiboken6,
or ffmpeg.exe/ffprobe.exe and six FFmpeg DLLs in bin. SOURCES contains concrete
rebuild/relink inputs for FFmpeg and its static LGPL encoder. No application
signature enforcement or private installation key prevents replacement.
Windows directory permissions apply. Normal app execution does not require
elevation; replacing Program Files files can require installation privileges.
Do not delete downloaded videos/configuration. Keep notices and disclose source
modifications when redistributing modified libraries. The application does not
prohibit reverse engineering to debug modifications of these libraries.

This is direct accompanying source provision, NOT a binding three-year written
offer, a fabricated offeror/contact, or a promise of a future source service.
Source archives contain unbuilt tests/examples/platform files; their presence
is not a claim those components are compiled into the Windows runtime.

PUBLIC DISTRIBUTION NEEDS LEGAL REVIEW: final Qt/PySide LGPL source/replacement
terms and Microsoft Distributable Code downstream conditions require
professional review. Inno commercial use is a separate business review item.
Native material existence and a successful rebuild are technical evidence,
not a legal opinion that all distribution terms have been fulfilled.
