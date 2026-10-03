# B4.2 clean Windows final validation

2026-10-02 · `codex/b4-2-final-release-gate`.

**Clean Machine = NOT TESTED. P1-1 remains open.**
没有进入独立 Windows Sandbox/新 VM/无开发环境 PC。当前开发机 PATH 隔离与本机运行结果没有替代独立验收。
此前用户确认暂无独立环境、保留 P1；本阶段没有取得新的独立环境。

## Environment evidence

当前主机 Windows 11 Pro 10.0.26200 / x64，普通非管理员用户。
`Containers-DisposableClientVM.InstallState=2`，WindowsSandbox.exe 不存在；
Get-VM、VBoxManage、vmrun 未检测到，没有可用且已实际启动的独立环境。
[Read-only capability evidence](evidence/b4_2-environment.json)。
没有启用 Windows feature、安装 runtime/虚拟机、修改 PATH/执行策略、关闭安全机制或重启主机。

| Prerequisite | Independent Windows | Existing host where.exe evidence |
|---|---|---|
| Windows version / architecture | NOT TESTED | 11 Pro10.0.26200 / AMD64 |
| python | NOT TESTED | PATH entries exist, including Python311/313 and WindowsApps alias |
| py | NOT TESTED | Windows launcher/PATH entries exist |
| yt-dlp | NOT TESTED | Python311/313 Scripts entries exist |
| ffmpeg | NOT TESTED | D:\ffmpeg and DouK-Downloader entries exist |
| ffprobe | NOT TESTED | same developer-host tool locations |
| deno | NOT TESTED | NOT FOUND on host PATH |

这是开发机实况，不能把 guest 从未运行改写为 NOT INSTALLED。
脚本没有执行 Python WindowsApps alias，避免触发 Microsoft Store。
完整 host PATH/dependency evidence：[kit report](evidence/b4_2-host-kit-report.json)。

## Release test kit

`release-test/` 实际准备：MediaDownloader-Portable.zip、MediaDownloader-Setup.exe、checksums.txt、
clean_machine_test.ps1、CLEAN_MACHINE_CHECKLIST.md。两个 generated binary artifacts 不进入 Git。
build_windows.py 每次成功构建同步 ZIP/Setup/checksums，脚本/checklist 为受版本控制的可复用材料。

脚本读取系统信息、逐个执行 where.exe、核对真实 ZIP/Setup SHA256、调用用户提供 EXE 的已有
--diagnostics 采集实际版本/路径、观察当前进程 executable path；只写报告/应用正常诊断数据。
不安装/解压/卸载依赖、不改系统环境/执行策略、不杀进程/删除目录、不采集 Cookie/header/token。
报告始终保留 IndependentEnvironment=NOT VERIFIED、CleanMachine=NOT TESTED；人工 checklist 决定功能结果。

在 Windows PowerShell5.1 实际运行 script：最终两项 checksum Match=true，两个 app mode 正确，
FFmpeg/FFprobe/Deno PathsWithinRoot 均 true；这是 **host collector validation**，不是 Clean PASS。
141 个自动测试含三个 script checks：前置报告不虚构 PASS、missing EXE 可诊断、篡改文件 checksum 为 false。
发现并修复跨 PowerShell 启动的 PSModulePath 继承导致 Get-FileHash 不加载问题，显式加载当前 host 的
内置 Utility module，无环境修改。初次失败日志保留，最终 retest PASS。

## Final local frozen checks versus independent acceptance

最终 ZIP 解压到 `D:\下载测试\YouTube视频\B4_2 Portable 验证\MediaDownloader-Portable`；
最终 Setup 实际安装到 `D:\下载测试\YouTube视频\B4_2 Installed 验证`。
测试使用真实 GUI/Manager acceptance runner，target PATH=`C:\WINDOWS\System32;C:\WINDOWS`。
host Python/fixture generator/proxy server 仅是验证驱动；不是目标 EXE 的 runtime 依赖。
独立 guest 必须按 kit checklist 双击/UI 操作，不依赖此 host Python runner。

| Required item | Final local Portable | Final local Installer | Independent Windows |
|---|---|---|---|
| Application Launch / Health | PASS | PASS | NOT TESTED |
| bundled yt-dlp2026.8.19 | PASS, embedded package | PASS | NOT TESTED |
| bundled FFmpeg / FFprobe | PASS, actual n8.1.3-14-g330caae0c1-20261001 | PASS | NOT TESTED |
| bundled Deno2.9.7 / EJS0.8.0 | PASS | PASS | NOT TESTED |
| actual runtime paths within package | PASS | PASS | NOT TESTED |
| real public Preview | PASS | PASS | NOT TESTED |
| 1080P complete download | PASS | PASS | NOT TESTED |
| 4K metadata / selection | PASS,401+251 /2160P | PASS | NOT TESTED |
| 8K metadata / Best Quality | PASS,571+251 /4320P | PASS | NOT TESTED |
| Audio Only | PASS, actual MP3 | PASS | NOT TESTED |
| Cancel / active exit | PASS, cancelled/children0 | PASS | NOT TESTED |
| Retry / resumed completion | PASS, controlled partial transfer | not separately required; Portable satisfies at-least-one | NOT TESTED |
| Save / exit / restart / Settings | PASS | PASS | NOT TESTED |
| History persistence | PASS | PASS | NOT TESTED |
| Chinese / space paths | PASS, actual download/package path | PASS | NOT TESTED |
| active-download Crash Recovery | PASS | at-least-one satisfied by Portable | NOT TESTED |
| Install / Start menu / selected Desktop shortcut | N/A | PASS | NOT TESTED |
| normal runtime without elevation | PASS | PASS; CURRENTUSER install | NOT TESTED |
| standard uninstall: directory/key/shortcuts | N/A | PASS | NOT TESTED |
| user videos/config after uninstall | N/A | PASS, SHA unchanged | NOT TESTED |
| full Portable directory deletion | NOT TESTED | N/A | NOT TESTED |

没有新一轮完整4K/8K下载，符合本阶段要求；8K 当前结论只为真实 metadata/selection，
B4 完整8K probe/decode证据不改写。没有 upscale、视频重压缩、降低 FPS/分辨率。

## Exact runtime paths

| Runtime | Portable | Installed during test |
|---|---|---|
| yt-dlp | D:\下载测试\YouTube视频\B4_2 Portable 验证\MediaDownloader-Portable\MediaDownloader.exe!PYZ.pyz/yt_dlp | D:\下载测试\YouTube视频\B4_2 Installed 验证\MediaDownloader.exe!PYZ.pyz/yt_dlp |
| FFmpeg | D:\下载测试\YouTube视频\B4_2 Portable 验证\MediaDownloader-Portable\bin\ffmpeg.exe | D:\下载测试\YouTube视频\B4_2 Installed 验证\bin\ffmpeg.exe |
| FFprobe | D:\下载测试\YouTube视频\B4_2 Portable 验证\MediaDownloader-Portable\bin\ffprobe.exe | D:\下载测试\YouTube视频\B4_2 Installed 验证\bin\ffprobe.exe |
| Deno | D:\下载测试\YouTube视频\B4_2 Portable 验证\MediaDownloader-Portable\bin\runtime\deno.exe | D:\下载测试\YouTube视频\B4_2 Installed 验证\bin\runtime\deno.exe |

`!PYZ.pyz/yt_dlp` 是实际 archive member notation；没有磁盘上的 yt-dlp.exe。
actual payload inventory 确认包存在，实际 Preview/Download 使用此内嵌包和 frozen path resolver。
Health 执行 bundled 工具版本命令，实际下载/合并/媒体 probe均成功；下载期采集进程完整 executable path。
未声称在独立环境观测过所有 Windows system DLL load locations。

## Exit, deletion, crash and uninstall evidence

最终 Portable 正在下载时观察 PID8392，partial2096128 bytes，执行 `taskkill /PID 8392 /T /F`。
强制结束的是已观察到的 app 进程树（包含 worker），随后同一 EXE 重启，JSON可读且 Settings保留，
history19→20，中断条目恢复 cancelled，Health READY。单独 Cancel→Retry 完成并从2097152 bytes续传。
不声称仅杀主进程后 orphan 自动消失。最终 installed 正常 restart 的35条 history保持 terminal。

最终 Setup 安装/卸载 exit0，普通用户无 required elevation，开始菜单/桌面 shortcut targets真实正确，
标准 unins000.exe 卸载后安装目录、两shortcut及HKCU卸载项不存在。
Settings、History、这次完整1080P媒体的 SHA256 与卸载前一致：User configuration intentionally preserved。
最终观察 MediaDownloader/FFmpeg/FFprobe/Deno named processes=0。

Portable测试副本保留，没有完整目录删除 PASS 证据。
旧B4自动审批 blocked by policy仅记录为旧环境限制，不算产品缺陷，也未绕过原拒绝。
只有进入独立 guest、实际关闭/查进程/人工删除整目录后，才能关闭该验收项；Sandbox自动销毁不替代删除检查。

最终精简可审阅证据：[regression](evidence/b4_2-regression.json)。完整原始 evidence在
`D:\YouTube视频下载\B4_2 evidence\portable-runtime-final`、`installed-runtime-final`、
`portable-crash-final`、`installed-persistence-final`、`uninstall-final.json`。
本地状态保持 PASS；Clean Machine、Portable Delete、clean Crash/Uninstall 均保持 NOT TESTED，P1-1不能关闭。
