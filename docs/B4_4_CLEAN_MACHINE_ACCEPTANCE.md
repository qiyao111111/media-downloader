# B4.4 Clean Machine Acceptance

日期：2026-10-02。分支：`codex/b4-4-clean-machine-acceptance`。
基线：`fc4b99977b01effcd9d79c8b3a1101b6e2c7cabf`（B4.3）。

**B4.4 Result: CONDITIONAL PASS**。本阶段完成测试包与取证准备，未完成独立 Windows 运行验收。

| Gate | Result | 依据 |
|---|---|---|
| Technical Release Gate | PASS | 保持 B4.3 已验证技术结果；现有 151 测试再次通过，发行文件哈希一致 |
| Clean Machine Gate | NOT TESTED | 本次会话没有可实际使用的独立 Windows Sandbox/VM/PC |
| Public Distribution Gate | NEEDS LEGAL REVIEW | 保持 B4.3 状态；本阶段不进行 Qt/PySide6、Microsoft、Inno 法律判断 |

P0=0；P1 Technical=0；P1 Distribution=2。准备测试包不关闭独立环境验收阻塞项。
未启动 B5，未发布 v1.0。

## 环境可用性与证据边界

以下是**开发主机可用性检查**，不是目标干净 Windows 的验收结果：

| 检查 | 实际结果 |
|---|---|
| 开发主机 Windows | Microsoft Windows 11 专业版，10.0.26200 |
| 开发主机架构 | 64 位 |
| WindowsSandbox.exe | `C:\Windows\System32\WindowsSandbox.exe` 不存在 |
| 可用启动/管理命令 | 未发现 WindowsSandbox.exe、vmrun.exe、VBoxManage.exe、Get-VM |
| vmcompute 服务 | 本次查询未发现 |
| Sandbox 可选功能查询 | 请求的操作需要提升；功能状态未确认，未修改系统功能 |
| 独立 VM/另一台 PC | 本次会话没有提供可执行的环境 |

这些结果说明本次无法执行所需独立验收；不据此断言硬件永远不支持 Sandbox。
没有启用功能、重启系统、安装依赖或用本机 PATH 隔离替代独立环境。
[原始环境查询](evidence/b4_4/environment-availability.json)。

目标环境的以下字段全部保持 **NOT TESTED**，不是 NOT INSTALLED：

| 目标字段 | Result |
|---|---|
| Windows Version / Architecture | NOT TESTED |
| Python (`where.exe python`、`where.exe py`) | NOT TESTED |
| System yt-dlp | NOT TESTED |
| System FFmpeg | NOT TESTED |
| System FFprobe | NOT TESTED |
| System QuickJS (`where.exe qjs`) | NOT TESTED |

开发主机上的采集器自测保留实际 where 结果，明确标为 development-host-collector-self-test。
主机已经安装开发工具，不能充当干净环境证明。

## 已准备的完整测试包

测试包位于仓库的 `release-test/`，可整个复制到 Sandbox、VM 或另一台 PC：

| 文件 | 状态与用途 |
|---|---|
| MediaDownloader-Portable.zip | 已存在，B4.3 最终 Portable，哈希已复核 |
| MediaDownloader-Setup.exe | 已存在，B4.3 最终安装器，哈希已复核 |
| checksums.txt | 两项 SHA256 与文件、dist/release 一致 |
| clean_machine_test.ps1 | 已更新并自测，检测 Python/py/yt-dlp/ffmpeg/ffprobe/qjs |
| CLEAN_MACHINE_CHECKLIST.md | 已更新，独立环境逐步操作、结果表和证据要求 |
| MediaDownloader-Test.wsb | 已核对，仅只读挂载 release-test 到 C:\ReleaseTest |

[检查脚本](../release-test/clean_machine_test.ps1)、
[逐步人工验收清单](../release-test/CLEAN_MACHINE_CHECKLIST.md)、
[Sandbox 配置](../release-test/MediaDownloader-Test.wsb)。

脚本收集系统版本、架构、PATH 命令结果、发行文件哈希、实际 Health 版本/路径与进程 EXE 路径。
指定 PortableRoot 或 InstallerRoot 时通过发行 EXE 的既有 `--diagnostics` 入口生成诊断。
FFmpeg/FFprobe/QuickJS 的路径逐项检查是否处于指定发行根目录，并检查实际 portable/installed mode。
新增 Stage 参数仅给报告标记取证阶段，不会自动判定功能、环境身份或 Clean Machine PASS。

脚本不安装依赖、不修改 PATH/执行策略/安全设置、不控制进程、不删除目录；
只写报告并在指定应用时调用诊断。应用诊断按现有实现初始化自己的用户目录/日志，不能代替 GUI 功能验收。
不采集进程命令行、Cookie、认证头或浏览器数据库。

WSB 映射只读，因此清单所有调用均显式将输出放到 `C:\Acceptance\Reports`。
Portable 解压到可写 guest 目录，下载文件放到 `C:\Acceptance\Downloads`，均与待删除目录分开。
退出/删除/卸载后取证不传应用根参数，避免诊断重新启动已关闭的 EXE。
Sandbox 销毁前必须人工删除 Portable 并导出证据，自动销毁不能代替删除测试。

## 发行文件身份

本阶段没有重建或替换发行 EXE/ZIP。实际文件与 B4.3 最终 SHA256 一致：

| Artifact | Bytes | SHA256 |
|---|---:|---|
| MediaDownloader-Portable.zip | 249637159 | fd722b494469e4ddda7c3b604759e09599e6b8e14d4ead1fe12033f976c5c415 |
| MediaDownloader-Setup.exe | 237696616 | aa34f3fba9eddbd6b6662f34f2c773072039db6375d2c3edefe8a5bf341be8d7 |

已直接检查 ZIP 中的应用 EXE、portable.flag、FFmpeg、FFprobe、QuickJS、Python DLL/标准库、
Qt 核心 DLL/Windows platform plugin、EJS solver 文件。
文件存在和哈希一致是测试包准备证明，**不是独立环境运行或依赖隔离 PASS**。
yt-dlp 是 EXE 中内嵌 Python package，脚本 EmbeddedYtDlp 说明不是 archive-member 检验。
短时 native 进程可能未出现在单次快照中，必须保留 Health 路径/版本并按清单补充取证。
[实际哈希、ZIP member、WSB 和采集器自测记录](evidence/b4_4/kit-validation.json)。

## 独立 Windows 验收矩阵

以下所有结果均指**真正独立 Windows 环境**。B4.3 的本机结果不填入本表。

| Portable item | Result | 需要的证据 |
|---|---|---|
| Launch | NOT TESTED | 普通权限实际窗口 |
| Runtime Health | NOT TESTED | READY 与真实版本 |
| Runtime Isolation | NOT TESTED | Health 和实际应用/native 路径在发行根，无开发 runtime |
| Preview | NOT TESTED | 真实公开视频 formats |
| 1080P | NOT TESTED | 完整媒体、视频+音频、ffprobe、完整时长 |
| 4K Metadata | NOT TESTED | 真实 2160P format/selection |
| 8K Metadata / Best Quality=4320P | NOT TESTED | 真实 7680×4320 format 与自动选择 |
| Audio | NOT TESTED | 完整音频文件与 ffprobe |
| Cancel | NOT TESTED | 实际传输后取消、正确状态 |
| Retry | NOT TESTED | 重新启动并完成有效文件 |
| Persistence | NOT TESTED | 保存、退出、重启后设置/历史相同 |
| Chinese Path | NOT TESTED | 中文目录中实际下载文件 |
| Space Path | NOT TESTED | 带空格目录中实际下载文件 |
| Normal Exit / Remaining Processes | NOT TESTED | 应用/FFmpeg/FFprobe/qjs 无残留 |
| Portable Delete | NOT TESTED | 真实整目录删除、目录不存在、无残留进程 |

| Installer item | Result | 需要的证据 |
|---|---|---|
| Install | NOT TESTED | 安装目录、开始菜单及所选桌面快捷方式 |
| Launch | NOT TESTED | 普通运行不需要管理员权限 |
| Runtime Health | NOT TESTED | READY 与真实版本 |
| Runtime Isolation | NOT TESTED | 实际安装根内运行时路径 |
| Preview | NOT TESTED | 真实格式解析 |
| 1080P | NOT TESTED | 实际完整视频+音频 |
| Persistence | NOT TESTED | Settings Save / Restart / History Persistence |
| Uninstall | NOT TESTED | 文件/快捷方式/卸载项删除，下载视频大小/哈希不变 |

| Crash Recovery item | Result | 需要的证据 |
|---|---|---|
| Active download / forced termination | NOT TESTED | partial transfer、实际 PID 与进度 |
| Settings / History readable | NOT TESTED | 同一包重启后值和记录可读取 |
| Valid JSON | NOT TESTED | 两个 JSON 解析无错误 |
| Runtime Health after restart | NOT TESTED | READY |

## 回归与本次改动范围

`python -m unittest discover -s tests -p "test_*.py" -v`：
**Previous=151 PASS；New=0；Total=151 PASS；0 failures、0 errors、0 skips；13.355 秒**。
[完整测试输出](evidence/b4_4/unit-tests.txt)。

既有采集器前置测试按当前发行策略从 Deno 检查改为 QuickJS，并验证 Stage 与固定 NOT TESTED/NOT VERIFIED 边界。
缺失应用不崩溃、损坏文件哈希被发现等既有测试继续通过。没有删除测试或以 skip 掩盖结果。
本机采集器自测没有调用 Portable/Installer 功能，报告始终不声称独立环境 PASS。

只修改外部验收脚本、人工清单、相应既有测试并新增本报告/证据。
下载核心、UI、Format Selector、Runtime 策略、发行依赖和 Public Distribution Gate 没有改变。
151 单元测试和包身份复核不替代独立 Windows 的下载、持久化、删除、卸载与 Crash Recovery。

## Still Open

| Severity | Item | 当前影响 |
|---|---|---|
| P1 Distribution | 独立 Windows Portable / Installer 全套验收、Runtime Isolation、Portable Delete、Uninstall、Crash Recovery | Clean Machine Gate=NOT TESTED；拿测试包到独立环境逐项实测后才可关闭 |
| P1 Distribution | B4.3 保留的 Qt/PySide6、Microsoft 最终分发条款专业复核，Inno 商业事项 | Public Distribution Gate=NEEDS LEGAL REVIEW；本阶段不处理 |

只有人工清单全部必需项目真实通过且证据完整，才能将 Clean Machine Gate 改为 PASS。
本次保持 B4.4 CONDITIONAL PASS，不能进入 B5 或发布 v1.0。
