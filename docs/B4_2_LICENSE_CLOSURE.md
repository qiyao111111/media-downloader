# B4.2 distribution license closure

2026-10-02 · `codex/b4-2-final-release-gate` · base `6abfce53e45aeb177d8486560cf43510069a955f`.

**Public Release Gate = BLOCKED. Source obligations are not resolved.**
已补齐可明确对应的材料并重建内部 RC；没有以“版本一样”“GitHub 可找”或泛化 written offer 判 PASS。
B4.1 历史结论不改写。最终文件清单见 [distribution inventory](B4_2_DISTRIBUTION_INVENTORY.md)。

## Actual FFmpeg build and source chain

发行来源为 BtbN 的 `autobuild-2026-10-01-13-06`，Windows x64 shared 8.1 build。
实际命令的完整输出：

- [ffmpeg-version.txt](evidence/ffmpeg-version.txt)
- [ffmpeg-buildconf.txt](evidence/ffmpeg-buildconf.txt)
- [ffmpeg-license.txt](evidence/ffmpeg-license.txt)
- [ffprobe-version.txt](evidence/ffprobe-version.txt)

版本 `n8.1.3-14-g330caae0c1-20261001`，GCC 16.2.0，主源码
`330caae0c1acccd2222edc52a05940c574561ce5`。配置含 `--enable-version3 --enable-shared
--disable-static --pkg-config-flags=--static`，没有 `--enable-gpl/--enable-nonfree`。
`-L` 声明 FFmpeg 本身为 LGPLv3-or-later；**不能据此把静态依赖和组合二进制全部判为 LGPL**。
`--disable-static` 控制 FFmpeg 自身 libraries，不会阻止外部 `.a` 被静态链接。

固定主源码、BtbN recipes、完整实际 configure 输出随包。按
[FFmpeg 官方复核说明](https://www.ffmpeg.org/legal.html)，还需匹配外部库对应源码及实际编译方式；
实际 GPL/LGPL 条款以随包原文为准，本报告不把官方 checklist 等同于许可证全部条款。

新增追踪 [CI run 36860751422](https://github.com/BtbN/FFmpeg-Builds/actions/runs/36860751422)：
recipes revision `e88e49f624457c455700b058f0a84ca87d499cc2`；target-image job `110365737251`，
FFmpeg job `110370083192`。下载实际 artifact `11162774383`，10 个 EXE/DLL 与 bundled files
逐文件 SHA256 一致，见 [CI identity](evidence/b4_2-ffmpeg-ci-identity.json)。
CI ZIP 与发布 ZIP archive digest 不同，不能声称两个 ZIP 完全一致；内部这 10 个二进制一致。

日志记录 avformat target 链接 Chromaprint/FFTW3，以及 cairo/glib/pango、lilv/serd/sord/sratom/zix、
Rust/toolchain 等传递候选。128 个 `-l` 项包括 Windows system imports，不能把所有项当作独立发行库。
脱敏摘要与日志 digest 见 [CI evidence](evidence/b4_2-ffmpeg-ci.json)；原始 CI 日志仅留在 `.tools/b42-ci`，
没有把 CI 授权头、临时下载签名或整份环境日志提交到项目/发行包。

**关键新增：**实际 target recipe `50-chromaprint.sh` 使用 `-DFFT_LIB=fftw3` 并静态链接。
Chromaprint revision `aed8eba2202dd9d7b3b0a56c77904cc805490d72` 原文给出 MIT + LGPL2.1，
同时明确要求考虑所选外部 FFT 的许可；FFTW3 revision
`93ed4c786934aec9946f8dda4b4e3eb08f8be41c` 的 COPYRIGHT 声明 GPL-2.0-or-later。
两份固定源码、FFTW COPYRIGHT/COPYING、Chromaprint LICENSE、完整 LGPL2.1 原文已补入包中。
FFTW recipe 的生成步骤和 `sed` 修改保留在固定 recipes 中；没有声称所有生成文件、resolved Rust
依赖或 provider patches 已全部重建并验证对应。

组合二进制的适用 GPL/LGPL 路径与修改披露范围为 **NEEDS LEGAL REVIEW**。
没有 FFTW 替代授权证据，不声称商业授权，也不擅自给整个应用重新指定 GPL 许可证。
完整对应源码/实际第三方 notices 缺口使这一组件的公开发行状态仍为 **BLOCKED**。

同 run 的 `download-cache` artifact `11161508103` 在审计时存在且未过期，约 2,206,711,199 bytes。
尝试 HTTP range 读取 inventory，服务返回 200，未继续整包下载；缓存内容/目标归属未建立。
这不是“不存在源码”的证据，也不是已提供完整 CS 的证据。有限保留期的 Actions cache 不是本项目
已落实的持续 source distribution service。继续关闭此项需要完整匹配/保存目标源码及依赖、构建/修改材料，
按适用 GPL/LGPL 条款同位置提供，或建立实际可履行的合法 written offer。

## Qt / PySide6 / Shiboken

实际版本均为 6.11.2。直接 Python imports 为 QtCore/QtGui/QtWidgets/QtNetwork；发行 DLL 为
Qt6Core/Gui/Network/Widgets/OpenGL/Svg，另有实际平台、样式、SVG/imageformats、TLS 等 plugins。
每个 exact file/来源/SHA 见 inventory。Qt6OpenGL 是 QtBase 的动态库，即使应用不用 OpenGL widget，
仍真实随包，不能删出许可清单。未发现 bundled GPL-only Qt module；QtPdf、VirtualKeyboard、
QML/Quick 等不存在，不把整个 PySide6_Addons wheel 的全部模块列为分发。

使用上述选定模块的 LGPL-compatible 开源路径；完整 LGPL3、GPL3 及适用第三方原文、
QtBase/QtSvg/QtImageFormats/PySide exact source snapshots 随包。
源 metadata 仅保留选定 Windows 模块的 attribution 与其明确引用的原始完整文本；
源码 archive 自身保留全部原始内容，但不把测试/示例/其他平台源文件当作独立 Windows runtime。
选定 metadata 是源候选清单，不能自动证明每项都编入官方 wheel。

PyInstaller **onedir**：Qt/PySide/Shiboken DLL/PYD/plugins 位于可单独替换目录，应用无私有签名校验/安装密钥；
source-offer/README.txt 给出替换路径，并允许调试修改库所需的 reverse engineering。
这提供了实际技术结构与源码访问，不等于已证明 LGPLv3 §4(d)/§4(e)、GPLv3 §6 的全部适用条件。
官方 wheel 的第三方静态包含/完整对应 build 材料，以及此 combined-work 分发/替换方式的条款适用，
保留 **NEEDS LEGAL REVIEW**，阻塞公开发行 PASS。没有假造 commercial Qt entitlement。

依据 [Qt Licensing](https://doc.qt.io/qt-6/licensing.html) 和
[Qt for Python grants](https://doc.qt.io/qtforpython-6/licenses.html) 区分模块/第三方许可；
具体 6.11.2 判断以保存的 exact source grants 为准，不拿在线更新文档替代固定版原文。

## Mesa / LLVM file-level finding

B4.1 的 `_internal/PySide6/opengl32sw.dll` 与当前 PySide wheel 的文件 SHA256 完全一致：
`34b444c016289b560662ff896deceb7f4b2c0723aed3d319ae167c9186ce42b3`。
这明确定位到 Qt wheel 可选软件渲染器；不是仅字符串扫描。
另外检查到官方历史 prebuilt 下载文件与此 DLL digest 不同，没有误认精确来源。

应用为 QWidget/raster，无 OpenGL widget/context 代码。本阶段在 spec 排除该可选 DLL；
实际 ZIP、Setup payload 均缺此文件，真实 GUI 与核心 smoke PASS。
证据见 [renderer exclusion](evidence/b4_2-renderer-exclusion.json)。该单独 renderer 的发行义务
**NOT APPLICABLE**；不把它的独立 Mesa/LLVM notices 混入最终 runtime 清单。
这不证明 FFmpeg/Deno 内部没有 LLVM 相关代码，相关 opaque transitive inventory 仍属于各自未关闭项。

## Python and Microsoft

实际 Python 3.13.13，`python313.dll/python3.dll`、stdlib/PYD 来自同一安装，完整 PSF/historical
LICENSE、exact Python source、incorporated-software notices 随包。OpenSSL3.0.19、SQLite3.50.4、
Expat2.7.5、zlib1.3.1、libbzip2/libffi/liblzma/libmpdec/HACL 分开记录；非自报版本标明 pin 来源。
PyYAML6.0.3 的实际 `_yaml` 返回 LibYAML0.2.5，新增 exact upstream MIT copyright/license。

实际 VC DLL 位于 Python root、PySide6、Shiboken 三处。root VCRUNTIME 14.42.34438.0，
wheel VC files 14.44.35211.0。文件字节与各自 build input SHA 相同，来源见
[native origins](evidence/b4_2-native-origins.json)，不是仅看到 Microsoft 字符串。
Python Windows LICENSE 的 Additional Conditions/Distributable Code 下游保护条款、对应 wheel
redist entitlement 及当前 MIT-only installer agreement 的满足方式为 **NEEDS LEGAL REVIEW**。
该具体专业判断阻塞公开发行 PASS；没有声称已持有 Visual Studio entitlement。

## Deno / EJS / installer engine

实际 Deno2.9.7 EXE 自报 V8 `15.0.245.2-rusty`、TypeScript6.0.3。固定 direct MIT LICENSE、
Cargo.lock、TypeScript Apache2 完整许可及实际编译器 Microsoft copyright header、Node/Undici
类型声明 MIT 文本均已随包。实际源 `cli/tsc/mod.rs` 将 compiler JS 和 Node declarations 嵌入；
这几项有源码证据，不是无差别将所有 Cargo package 当 runtime。

Cargo.lock 含 1,128 records，混有 tests/build/other-target；release assets 未提供匹配这个 Windows EXE
的完整 transitive notice inventory。V8/ICU/Rust 等目标二进制对应版权/条款仍未完全匹配保留，
因此 Deno = **BLOCKED**。不以一个 MIT LICENSE 宣布整个 executable PASS。

EJS0.8.0 是独立 Python/data solver；lib.min.js 原始 Meriyah6.1.4 ISC / Astring1.9.0 MIT
完整 header 保留、另有 notice copy；实际发行存在性/digest验证 PASS。

Inno Setup6.7.3 的生成 Setup/uninstaller engine 实际随包，ISCC compiler 不随包。
exact build-package license 新增到 LICENSES；其原始二进制 copyright/web-address retention 条款
单列 **NEEDS LEGAL REVIEW**：custom version resource 的 Company/Version 不证明完整保留原始 notices。
没有修改 engine 源码，也没有将其误列为 runtime 下载依赖。

## Source provision and disposition

source-offer/README.txt 提供已随包 source access 和 shared-library replacement 信息，明确不是
GPL §6(b) 的三年 binding written offer，没有发明主体、联系方式或服务承诺。
采用实际提供源码/同一下载位置的方向，但 FFmpeg 完整 CS 未关闭，因此不能据此公开发行。
所有取得的 source/archive digest 已固定并与实际包验证。未把无关依赖的几百份 grant 填进 LICENSES。

**P1-2 保留。**待办：完成 FFmpeg 组合许可/完整对应源码、Deno target-specific notices、
Qt/MS/Inno 上述具体条款复核。公开发行为 BLOCKED，不进入 B5，不发布 v1.0。
