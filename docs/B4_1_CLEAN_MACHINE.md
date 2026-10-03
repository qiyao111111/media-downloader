# B4.1 Clean Windows gate

Date: 2026-10-02. Branch: `codex/b4-1-release-gate`.
Base: `7fac14876278fe0aaafddcea7f90bb8bb9846713`.

**Clean Machine = NOT TESTED. Severity = P1. Public release remains blocked.**
用户明确回复：“目前没有独立环境，保留 P1”。本阶段没有安装开发依赖到另一台机器，
没有启用 Windows 可选功能或请求重启，也没有把本机 PATH 隔离改称干净机器验收。

## Environment availability

本机为 Windows 11 Pro 10.0.26200 / AMD64，普通用户。它是开发机，存在 Python、项目源码和构建工具。
`WindowsSandbox.exe` 不存在；Sandbox Appx 未找到；`Containers-DisposableClientVM` 的
`Win32_OptionalFeature.InstallState=2`（disabled）；未发现可用 Hyper-V VM、VirtualBox 或 VMware。
`HypervisorPresent=True` 本身不能证明有可启动的独立 Windows 环境。

| Clean-environment preflight | Recorded result |
|---|---|
| Windows version / architecture | NOT TESTED — no independent guest |
| `where python` | NOT TESTED |
| `where py` | NOT TESTED |
| `where yt-dlp` | NOT TESTED |
| `where ffmpeg` | NOT TESTED |
| `where ffprobe` | NOT TESTED |
| `where deno` | NOT TESTED |
| Python / yt-dlp / FFmpeg / Deno installed in guest | NOT VERIFIED |

不能在没有进入 guest 时填写 NOT INSTALLED。以上不描述开发机的安装状况。

## Independent gate checklist

| Required check | Portable clean Windows | Installer clean Windows |
|---|---|---|
| Launch / runtime versions | NOT TESTED | NOT TESTED |
| bundled yt-dlp / FFmpeg / FFprobe / JS | NOT TESTED | NOT TESTED |
| runtime isolation / full paths | NOT TESTED | NOT TESTED |
| Preview / full 1080P | NOT TESTED | NOT TESTED |
| 4K metadata / selection | NOT TESTED | NOT TESTED |
| 8K metadata / Best = 4320P | NOT TESTED | NOT TESTED |
| Audio / Cancel / Retry | NOT TESTED | NOT TESTED |
| Settings / History restart persistence | NOT TESTED | NOT TESTED |
| Chinese download directory | NOT TESTED | NOT TESTED |
| active-download crash / restart | NOT TESTED | NOT TESTED |
| Install / shortcuts / normal nonadmin run | N/A | NOT TESTED |
| Exit / residual-process check / full folder deletion | NOT TESTED | N/A |
| Uninstall / shortcuts / key removal / videos preserved | N/A | NOT TESTED |
| optional full 4K | NOT TESTED | NOT TESTED |

所有 Clean Machine 必需条件仍待独立环境实际运行。B4 的完整 8K 下载证据保留，不要求重复全片 8K。

## Procedure ready for a clean Windows guest

1. 记录 Windows version、architecture、表中各个 `where` 命令的结果。
   若没有则记 NOT INSTALLED；若意外存在则列出路径、说明来源，不能据此推定隔离已完成。
2. 只复制最终 `dist/release/MediaDownloader-Portable.zip` 和 `MediaDownloader-Setup.exe`，
   先核对 `checksums.txt`。不复制源码、不安装 Python/FFmpeg/yt-dlp/Deno、不修改 PATH。
3. 解压 ZIP、双击 EXE；记录 Runtime Health 版本与实际路径。独立观察 UI，并完成上表 Portable 项。
   真实 8K 源为 `https://www.youtube.com/watch?v=E86EwGT_c2M`，Preview 须选出真实 4320P。
4. 关闭应用，检查 Task Manager 无该次测试残留的 MediaDownloader、FFmpeg、FFprobe、yt-dlp、Deno。
   人工删除整个 Portable 目录并确认删除成功。即使 Sandbox 关闭会销毁，也必须先完成此步骤。
5. 在同一 guest 或新的干净 snapshot 安装 Setup，检查开始菜单和选中的桌面快捷方式；
   正常 EXE 必须无需 Run as Administrator。完成 Installer 的 Preview/1080P/持久化检查。
6. 至少一包执行：修改 Settings、启动下载、强制结束、重启；检查 JSON 可读、history 恢复、Runtime Health。
7. 标准 Windows 卸载：程序目录、快捷方式、卸载项消失；下载视频不删除。
   配置保留策略为 **User configuration intentionally preserved**。
8. 将 guest 前置记录、运行路径、媒体 probe、状态、重启与删除/卸载证据纳入报告后再重新判 gate。

## Local evidence boundary

本机已用最终 ZIP 和 Setup 执行真实 frozen GUI/Manager 测试；目标 EXE 的 PATH 仅为
`C:\WINDOWS\System32;C:\WINDOWS`，清除 Python/Qt 环境覆盖。
`tests/validate_b4_frozen.py` 的父 Python 与 loopback HTTP/proxy 是测试 fixture，不由应用调用。
这能证明当前调用路径来自发行包；不能证明另一台无开发环境的机器可运行。

| Local check | Portable | Installer |
|---|---|---|
| Launch / health / bundle paths | PASS | PASS |
| 1080P / 4K metadata / 8K metadata | PASS | PASS |
| Audio | PASS | PASS after 403 retest |
| cookies.txt / HTTP / SOCKS5 / SOCKS5H | PASS | PASS |
| Cancel / active exit | PASS | PASS |
| restart / Settings / History | PASS | PASS |
| active forced-stop recovery / fixture retry | PASS | not repeated; Portable satisfies at-least-one local check |
| Install / selected shortcuts / nonadmin operation | N/A | PASS |
| Uninstall / configuration and video retention | N/A | PASS |
| Portable complete directory delete | NOT TESTED | N/A |

Portable 删除在 B4 曾被自动审批拒绝（`blocked by policy`），未通过另一种删除工具绕过。
本次未执行删除；副本保留。这是验收证据缺口，不是已证实的产品删除故障。
本机完成后无 MediaDownloader/FFmpeg/FFprobe/Deno 残留进程，仍不能单凭此判 Portable Delete = PASS。

证据：`D:\YouTube视频下载\B4_1 evidence`；详情见 [release gate](B4_1_RELEASE_GATE.md)。
