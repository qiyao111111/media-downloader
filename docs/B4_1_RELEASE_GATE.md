# B4.1 Release Gate Validation

Date: 2026-10-02. Branch: `codex/b4-1-release-gate`.
Base: `7fac14876278fe0aaafddcea7f90bb8bb9846713`; initial workspace clean.

**B4.1 Result = CONDITIONAL PASS. P0 = 0; release-blocking P1 = 2.**
本机最终包运行与回归通过；独立 Windows 验收缺失、公开转发行许可义务未全部关闭。
没有进入 B5，没有发布 v1.0，没有 UI/selector/下载核心/品牌修改。

## Scope and packaging correction

文件级审计发现 `collect_all('yt_dlp')` 收集 `yt_dlp.__pyinstaller` 构建 hook，继而把
PyInstaller GPL analysis/build modules 放入 PYZ。这些不是应用 runtime，不能直接套用 bootloader exception。
只在 spec 排除上述构建模块。bootloader/loader 和实际独立 runtime hooks 保留并按原 grant 提供许可。
另排除 app 没有加载的 Qt `.qm` 翻译文件，避免误列未使用组件。没有移除应用语言字符串或改变 UI。

替换旧的泛化 license collector：按实际 PYZ/native payload 收集文本、源 archive、版本、hash、
buildconf 与 Qt attribution。校验下载 SHA256 后才替换缓存，失败保留旧文件并清除临时文件。
加入具体未关闭义务的 NOTICE 和本地 source access/replacement 文档；不发明有效 written offer。

与 B4 已测试最终副本比较：43 个 application PYZ modules 的 raw bytes、11 个 bin native runtime
文件 SHA256 均相同（core-equivalence.json）。整体 PYZ 因移除构建依赖有意不同；不能使用
“整 EXE 完全相同”来描述本次重建。所有 app/core/gui/models/services/configs 源文件没有修改。

## Gate results

| Gate | Result | Release impact |
|---|---|---|
| Independent clean Windows Portable / Installer | NOT TESTED | P1; user explicitly accepts retaining it |
| Local frozen Portable / Installer runtime smoke | PASS, one upstream 403 retested | local evidence only |
| Local package paths / Windows-only PATH | PASS | does not substitute for independent environment |
| License matrix / file inventory | COMPLETED, ACTION REQUIRED rows remain | P1 licensing remains |
| NOTICE / LICENSES packaged in actual ZIP and installed Setup | PASS for retained materials | missing correspondence/notice obligations still block release |
| Full corresponding source / complete target-specific notices | ACTION REQUIRED | no public release clearance |
| SHA256 rebuild and verification | PASS | final artifacts only |
| Existing 135 + new source-verification tests | 138 PASS | no skipped unittest cases |

## Final local frozen regression

普通用户 Windows 11 Pro 10.0.26200 / AMD64。实际 GUI/Manager acceptance runner;
target PATH=`C:\WINDOWS\System32;C:\WINDOWS`，清除 Python/Qt plugin 环境覆盖。
host Python、FFmpeg fixture generator 与 loopback server 仅用于测试数据/转发，不是目标 EXE 依赖。

| Check | Portable | Installer | Actual evidence |
|---|---|---|---|
| Launch / Runtime Health | PASS | PASS | application/config/temp/download READY |
| yt-dlp | PASS, 2026.8.19 | same | embedded package in EXE PYZ; no system yt-dlp executable |
| FFmpeg / FFprobe | PASS | PASS | n8.1.3-14-g330caae0c1-20261001, bundle bin absolute paths |
| Deno / EJS | PASS, 2.9.7 / 0.8.0 | same | bundle bin/runtime/deno.exe and solver data |
| Preview | PASS | PASS | real E86EwGT_c2M formats |
| 1080P complete | PASS | PASS | 399+251; ffprobe 1920×1080 AV1 + Opus, duration 154.774s |
| 4K metadata / selection | PASS | PASS | actual 2160P, 401+251 |
| 8K metadata / Best Quality | PASS | PASS | actual 4320P, 571+251; real option label |
| Audio Only / MP3 extraction | PASS | PASS after fresh-parse retest | final MP3 exists; bundled FFmpeg probe |
| Cancel / active exit | PASS | PASS | states cancelled, shutdown children=0 |
| Retry / resumed fixture download | PASS | not repeated | actual cancellation, retry=true, resume_first_bytes=2097152, completed |
| cookies.txt | PASS | PASS | controlled Cookie-required server, both Preview/Download authenticated |
| HTTP / SOCKS5 / SOCKS5H | PASS | PASS | authenticated forwarding; all proxy_auth=true |
| Settings / History restart | PASS | PASS | real Save; retries=7/workers=1/path preserved; no autoqueue |
| Chinese / space directory | PASS | PASS | actual package/install/download paths contain Chinese and spaces |
| Active-download forced termination / recovery | PASS | at-least-one check satisfied by Portable | interrupted partial transfer >1 MiB; readable JSON; stale history -> cancelled; health READY |
| Normal runtime nonadmin | PASS | PASS | host nonadmin; Setup CURRENTUSER; no elevation needed to download |
| Install / Start menu / selected Desktop shortcut | N/A | PASS | real Setup exit 0, both .lnk observed |
| Standard uninstall | N/A | PASS | exit 0, program directory/shortcuts/uninstall key removed |
| User data / downloads after uninstall | N/A | PASS | settings/history/video hashes preserved |
| Complete Portable folder deletion | NOT TESTED | N/A | no independent environment; no policy bypass |

没有再次完整下载 4K/8K。此次 packaging-only 变更的 application/native bytes 一致，B4 的全片
4K/8K probe/decode 证据保持原历史；本阶段新的 8K 结论是 **metadata/selection PASS**，不是新一轮全片 PASS。
没有对视频降分辨率、降低 FPS、重编码或 upscale。

## Runtime paths actually resolved and executed

Portable root:
`D:\下载测试\YouTube视频\B4_1 Portable 验证\MediaDownloader-Portable`

Installer root during testing:
`D:\下载测试\YouTube视频\B4_1 Installed 验证`

| Runtime | Portable full location | Installed full location |
|---|---|---|
| yt-dlp | `D:\下载测试\YouTube视频\B4_1 Portable 验证\MediaDownloader-Portable\MediaDownloader.exe!PYZ.pyz/yt_dlp` | `D:\下载测试\YouTube视频\B4_1 Installed 验证\MediaDownloader.exe!PYZ.pyz/yt_dlp` |
| FFmpeg | `D:\下载测试\YouTube视频\B4_1 Portable 验证\MediaDownloader-Portable\bin\ffmpeg.exe` | `D:\下载测试\YouTube视频\B4_1 Installed 验证\bin\ffmpeg.exe` |
| FFprobe | `D:\下载测试\YouTube视频\B4_1 Portable 验证\MediaDownloader-Portable\bin\ffprobe.exe` | `D:\下载测试\YouTube视频\B4_1 Installed 验证\bin\ffprobe.exe` |
| Deno | `D:\下载测试\YouTube视频\B4_1 Portable 验证\MediaDownloader-Portable\bin\runtime\deno.exe` | `D:\下载测试\YouTube视频\B4_1 Installed 验证\bin\runtime\deno.exe` |

`!PYZ.pyz/yt_dlp` 表示 EXE 内嵌 archive member，不是虚构一个磁盘上的 yt-dlp.exe。
Health 运行 bundled 工具版本命令，download/probe 使用同一 frozen absolute-path resolver；
真实 ffprobe 文件已记录实际媒体结果。未把系统 DLL 加载来源全面观测/独立环境隔离标为 PASS。

## Persistence, crash, failures and credentials

Portable 强制结束：观察本次 EXE PID=5996，partial file 2096128 bytes；
`taskkill /PID 5996 /T /F` 强制结束该应用进程树（包含 worker），然后正常重启。
JSON settings/history 可读，retries/workers/path 保留，12 -> 13 条 history，新增中断条目被恢复为 cancelled。
未声称只 kill 主进程后所有 orphan 自动消失；本测试采用 Windows 进程树强制结束。
之后独立 slow fixture Cancel -> Retry -> Complete，first resume bytes=2097152。

Installer restart 前后 19 条 history 保持且 terminal；用户配置按产品策略保留。
真实卸载前后 settings/history 与本次 1080P 媒体 SHA256 不变；没有移除用户视频。
完成后观察无 MediaDownloader/FFmpeg/FFprobe/Deno 残留，Portable 副本仍保留。

首次 installed Audio 的数据请求收到 HTTP 403；程序进入 failed，不 crash。
重新提取同一源的 formats 后另一次真实 MP3 下载成功。首次结果不改写：
`installed-runtime/results.json` 保留 failed，`installed-retest/results.json` 为 completed。
这是已观察到的上游请求波动，P2 风险保留，未修改核心 options/selector。

首次 license build 因 Qt raw attribution 字符串含 literal newline 导致 JSON parser 失败；
修正非 strict metadata 解析，84 个原 metadata 文件解析且原文保留后 build PASS。
两个 host validation scripts 首次使用 GBK 默认编码/假定 history 实时更新而失败；
改为 UTF-8、依据 live partial file 与 nonterminal persisted record，保留失败日志后复测 PASS。
这些 driver 修正没有修改应用的失败/存储处理。

Portable/installed 应用日志扫描未发现 controlled cookie value、proxy password 或完整认证 header。
测试 cookies/proxy 是 loopback fixture，不能改写 B0.2 的个人浏览器登录态历史结果；
Chrome/Edge direct extraction 仍为 EXPERIMENTAL。未上传 Cookies 或读取浏览器密码。

## License gate and package validation

见 [license matrix](B4_1_LICENSE_MATRIX.md)：13 required fields、59 FFmpeg enabled dependency entries、
Qt raw source attribution index、每个实际 native file 的 component ownership。
依据实际 FFmpeg `-L/-buildconf`，为 LGPLv3-or-later shared build；不从通常 LGPL 推断。
Qt/PySide source and notices、Python exact source/incorporated notices、direct Deno/EJS/yt-dlp grants、
bootloader exception/runtime-hook copyright headers均进入 actual binary packages。

**公开发行仍阻塞**：FFmpeg 静态/传递依赖的完整对应源码与 notices，Deno target-specific
transitive notices，Qt Mesa/LLVM renderer 完整 provenance/notice 与 Microsoft downstream conditions。
矩阵对不能确定的具体条款标 NEEDS LEGAL REVIEW，不发明发行许可结论。
source-offer 文档提供实际本地源码访问，但明确不是有效三年 written offer，也不声称完整 CS 已交付。

ZIP/Setup 安装目录实际逐文件 SHA256 比对：1430 files PASS；source hash 11 items PASS；
GPL analysis modules absent；no compiled `.qm`；runtime hooks copyright files=8；
最长 bundle-relative path 101 chars，较深 source metadata paths已扁平化且原路径在 catalog 保留。
本机解压/安装成功；不能以此替代 Clean Machine。

| Final artifact | Bytes | SHA256 |
|---|---:|---|
| MediaDownloader-Portable.zip | 282005340 | 77f1a5eae4b40f2b2aedc3389f7c22c12303d11ca6ddc13ff7521a6d320d2285 |
| MediaDownloader-Setup.exe | 235909739 | 79dc3e8e09386cf588decf7d559c3de0bfe1c57ab31b4626405d8d7773fa6fed |

`dist/release/checksums.txt` 已重建，并与最终两个文件重新计算结果一致。
`dist/release/LICENSES`、`THIRD_PARTY_NOTICES.txt`、`source-offer` 为独立审计材料副本；
两个发行包也各含相同 license/notice/source access 内容。产物仅用于内部验证，未公开发布。

## Tests and evidence

`.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"`
**138 PASS / 9.885s / 0 skip** = 135 old + 3 source/cache integrity checks。
Final log: `D:\YouTube视频下载\B4_1-tests-final.log`。
真实 acceptance/packaging scripts 不混入 unittest 数量。

| Evidence under `D:\YouTube视频下载\B4_1 evidence` | Meaning |
|---|---|
| portable-runtime/results.json, summary.json, host-fixtures.json | 10 actual frozen cases, versions/paths, Cookie/proxy evidence |
| installed-runtime/same names | 10 cases, preserves first Audio 403 failure |
| installed-retest/results.json and audio probe | fresh extraction + actual MP3 completion |
| portable-crash-final/crash-recovery.json, restart, retry | active force-stop, persistence, recovery, cancel/retry |
| installed-persistence/persistence.json | restart settings/history verification |
| installer-metadata.json / uninstall.json | real install, nonadmin, shortcuts/key removal, user data retention |
| artifact-validation.json | actual ZIP vs installed payload, source digests, checksums |
| native-file-audit.json | every PE version resource/import list |
| core-equivalence.json | application modules/native runtime equivalence to B4 tested copy |

Build success log: `D:\YouTube视频下载\B4_1-build-retest.log`。
首次失败日志保留：B4_1-build.log、B4_1-artifacts.log、B4_1-crash.log、B4_1-crash-retest.log、
B4_1-installed.log；最终 retest evidence 与这些失败分开保存。

## Still open / release disposition

| Severity | Count | Unclosed item / public release impact |
|---|---:|---|
| P0 | 0 | no demonstrated frozen core regression |
| P1 | 2 | 1. independent clean Windows gate; 2. complete binary redistribution/source/notices/legal review. Both block public release PASS |
| P2 | 2 | upstream YouTube challenge / Chromium cookies limits (including observed 403); older player AV1/VP9/Opus compatibility |
| P3 | 1 | broad language switching remains partial; no B5 polish in this phase |

Portable directory deletion evidence is now explicitly included in clean-machine P1, not double-counted as an
independent product failure. B4's historical report/results remain unchanged. Optional Windows 10/Chinese
Windows username/all-users install coverage remains NOT TESTED.

Branch `codex/b4-runtime-packaging` stays at 7fac148; master stays at 0e42112dae627c10ce159ece0ef97594ccd27d39.
Work stops after the requested B4.1 test/docs/packaging commit. This conditional result does not authorize B5 or publication.
