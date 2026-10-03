# B4.2 Final Release Gate

2026-10-02 · branch `codex/b4-2-final-release-gate` · base `6abfce53e45aeb177d8486560cf43510069a955f`。
创建分支前 workspace clean；未修改原B4.1/B4/master分支。

**B4.2 Result = CONDITIONAL PASS. P0=0; P1=2. Public Release Gate = BLOCKED.**
本机最终 RC回归与发行文件验证通过；独立 Windows 和完整第三方公开发行义务未关闭，不能进入B5。
没有新功能、UI/selector/下载核心修改、平台/品牌开发或v1.0发布。

## Gate disposition

| Gate | Result | Evidence / public impact |
|---|---|---|
| Clean Windows Portable / Installer | NOT TESTED | no independent environment; P1-1 |
| Clean runtime isolation / Portable Delete / Installer Uninstall | NOT TESTED | local evidence cannot substitute; P1-1 |
| Clean persistence / Crash Recovery | NOT TESTED | local final checks PASS; P1-1 |
| Final local runtime/function smoke | PASS | both actual artifacts,10cases each |
| Final local install/uninstall/persistence | PASS | normal-user install, shortcuts/key/directory removed; user data preserved |
| Complete exact physical-file inventory | PASS | 1301files,80native,1347embedded modules |
| Complete transitive component/license inventory | BLOCKED | opaque FFmpeg/Deno mapping incomplete; P1-2 |
| Known texts/notices acquired and packaged | PASS for retained materials | 147 LICENSES files;16source provenance hashes verified |
| No known missing target-specific notices/texts | BLOCKED | cannot assert this gate true; FFmpeg/Deno incomplete |
| Corresponding source / valid source-offer | BLOCKED | complete FFmpeg external/transitive/generated sources unresolved |
| Qt/MS/Inno actual terms | NEEDS LEGAL REVIEW | specific clauses/provenance in closure report; public PASS blocked |
| Final ZIP/Setup SHA256 | PASS | regenerated + recomputed + test kit copies verified |
| Previous138tests | PASS | no old unittest skipped |
| New kit tests | 3PASS | real WindowsPS5.1 preflight/missingEXE/tamperedhash checks |
| P0=0 / P1=0 | P0=0, P1=2 | final PASS criteria not met |

## Packaging/material changes

Spec excludes optional Qt opengl32sw.dll software renderer; QWidget/raster application has no OpenGL widget/context
usage and actual GUI/runtime smoke remains PASS. No downloaded-runtime bytes changed.
Source collector now follows selected Windows-module attribution references and retains original referenced full texts;
full source archives preserve upstream source notices. Compiled translations/source-only unrelated standalone grants
are not listed as executable runtime dependencies. Unused commercial Qt texts are not presented as an entitlement.

Added actual LibYAML, embedded Deno TypeScript/Node/Undici notices, actual Inno generated-engine grant, and newly
confirmed Chromaprint/FFTW3 source/grants. Matching CI artifact proves ten FFmpeg native files are byte-identical;
FFTW GPL2+ combo scope is explicitly under review, rather than applying FFmpeg -L to every dependency.
NOTICE/source access documents accurately state open obligations and do not invent a written offer.

43application PYZ modules have identical raw bytes and11bin native files identical SHA to B4.1testedcopy:
[core equivalence](evidence/b4_2-core-equivalence.json)。app/core/gui/models/services/configs source files have no diff。
Tests/build/license/docs-only changes; no downgrade/upscale/transcoding introduced.

## Final local regression

Both final artifacts: actual GUI launch/Health,public Preview,1080P complete399+251,ffprobe1920×1080AV1+Opus,
4K metadata401+251,8K Best571+251/4320P,MP3Audio,controlledcookies.txt,authenticatedHTTP/SOCKS5/SOCKS5H,
Cancel/activeExit PASS。Final proxy_auth/cookie_authenticated all true; shutdown children=0。
Portable download crash,restart/readableJSON/recovery/Cancel→Retry PASS；Installer restart/persistence and normal
uninstall PASS，user settings/history/download hashes preserved。中文/空格实际路径PASS。
日志扫描3个app log未发现 controlled Cookie value/proxy password/完整Cookieheader；不冒充个人浏览器会话测试。
Chrome/Edge认证历史策略保持 EXPERIMENTAL，本阶段没有 Cookie extraction开发。

4K/8K不要求重新完整下载；B4完整probe/decode历史保持，本阶段8K只写metadata/selectionPASS。
`D:\YouTube视频下载\B4_2 evidence\portable-runtime-final`、`installed-runtime-final`保留实际完整结果。
精简final证据：[regression.json](evidence/b4_2-regression.json)。

## Final internal artifacts

| Artifact | Bytes | SHA256 |
|---|---:|---|
| MediaDownloader-Portable.zip | 274131685 | a85cc87f55149ed112aa6a974e48e2e8f0f2e85046f238f95b3e8ebec96a12c9 |
| MediaDownloader-Setup.exe | 230935228 | 7f2331714b7d352abaeddee585587d4b7a7d26c9f80845014c8ecc5bef679ccc |

在 `dist/release/` 和 `release-test/` 中均存在同一最终ZIP/EXE/checksums，重新计算SHA一致。
dist/release/LICENSES、THIRD_PARTY_NOTICES、source-offer为审计副本，且ZIP/实际Setup安装目录
真实包含同一材料，不是仅存在源码目录。实际逐文件比对1301项，16source hash，8runtimehook版权文件，
relative path最长80characters，finalrenderer/.qm/GPLanalysis modules均不存在。
Machine SBOM未生成：现有证据不足以可靠声明全部native静态依赖；完整文件清单代替伪造SPDX。
此内部RC公开发行BLOCKED；未上传/发布任何artifact。

## Tests and retained failed attempts

`.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"`：
**141PASS /18.516s /0skip** = previous138+new3。Log `D:\YouTube视频下载\B4_2-tests-retest.log`。
Actual frozen/artifact/crash scripts are separate integration evidence，不混入unittest计数。
Final successful build log：`D:\YouTube视频下载\B4_2-distribution-final-build.log`。

保留首次script运行的expectedmissingwhere stderr问题、checksum开始执行后暴露的Get-FileHash module
加载问题（B4_2-tests-final.log，140tests/2fail，后修复+新tampertest后141PASS）。没有把失败日志改成PASS。
一次临时persistence driver将os.environ转换dict后用SystemRoot大小写访问触发KeyError，尚未启动EXE；
改为原Windowscase-insensitive os.environ读取后真实restart PASS。旧日志B4_2-persistence-final.log保留，
成功为B4_2-persistence-retest.log。仅validationdriver修正，无应用存储/core修复。

许可材料取得/notice更新期间多次重建；只使用上表最终hash判定finalartifacts，旧hash不再是finalRC。
Final实包重新跑全部10case、activecrash/retry、install/persistence/uninstall和artifacthash检查。

## Still open

| Severity | Count | Item / public release impact |
|---|---:|---|
| P0 | 0 | no demonstrated frozen core regression |
| P1 | 2 | P1-1independentcleanWindows全部必需验收；P1-2FFmpeg/Deno完整source/notices与Qt/MS/Inno具体许可复核。Both block release PASS |
| P2 | 2 | inherited upstreamYouTube/challenge/Chromiumauthenticationlimits；olderplayerAV1/VP9/Opuscompatibility |
| P3 | 1 | inheritedpartiallanguageswitching；noB5polishperformed |

PortableDelete缺证据包含在P1-1，不另算产品缺陷；最终本机卸载PASS不改写cleanUninstall=NOTTESTED。
GPL/LGPL组合条款保留专业判断，当前缺完整source/notices使PublicRelease=BLOCKED。
没有宣称许可证禁止所有可合规分发方案，也没有据不完整材料认定本应用已被重新许可。
只有独立环境实际全部PASS、source/notices/legalgate关闭且P1=0，才可另行达到B4.2PASS。
完成本阶段提交后停止；不进入B5，不发布v1.0。

Reports:

- [Clean Machine Final](B4_2_CLEAN_MACHINE_FINAL.md)
- [Distribution Inventory](B4_2_DISTRIBUTION_INVENTORY.md)
- [License Closure](B4_2_LICENSE_CLOSURE.md)
