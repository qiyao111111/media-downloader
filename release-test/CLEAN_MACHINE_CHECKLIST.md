# B4.4 独立 Windows 人工验收清单

内部测试包。Public Distribution Gate = NEEDS LEGAL REVIEW，保持不变。
初始 Clean Machine Gate = NOT TESTED；未实际完成的项目不得填写 PASS。

## 1. 环境与前置检查

使用 Windows Sandbox、全新 VM 或没有开发环境的另一台 Windows PC。
记录测试人、日期、环境来源（Sandbox / VM 与 snapshot / PC）、Windows 版本、架构、网络条件。
开发机或开发机 PATH 隔离不能替代本验收。不得安装 Python/pip/PySide6/yt-dlp/FFmpeg/FFprobe/QuickJS/Deno/Node.js，
不得复制源码或修改 PATH、安全设置。

完整复制 release-test 目录，包括 ZIP、Setup、checksums.txt、检查脚本和本清单。
已有可用 Sandbox 时可双击 MediaDownloader-Test.wsb，它只读挂载测试包到 C:\ReleaseTest。
移动测试包后先核对 WSB HostFolder；仅挂载测试包，不得挂载开发源码。
WSB 不启用/安装 Sandbox，也不证明已运行 Sandbox。

在独立环境中建立 C:\Acceptance\Reports 和 C:\Acceptance\Downloads。
以下示例使用 C:\ReleaseTest；VM/PC 按实际测试包位置进入。
**报告、截图和下载文件均放在 Portable 目录外**，关闭 Sandbox 前将证据导出到持久位置。

在该环境允许执行本地脚本的普通 PowerShell 中运行：

```powershell
Set-Location 'C:\ReleaseTest'
.\clean_machine_test.ps1 -Stage preflight -OutputDirectory 'C:\Acceptance\Reports'
```

脚本逐项记录以下命令的返回码和原始路径，不执行 Python WindowsApps alias：

```powershell
where.exe python
where.exe py
where.exe yt-dlp
where.exe ffmpeg
where.exe ffprobe
where.exe qjs
```

预期 NOT FOUND。意外已有组件或 alias，注明来源；不存在组件本身不证明应用隔离。
确认 JSON 两项 ArtifactChecksums.Match=true。缺文件/不匹配时停止使用该包。
若执行策略拒绝脚本，记录 POLICY BLOCKED，按环境既有管理流程处理；本包不绕过或修改执行策略。
脚本仅取证，不安装依赖、结束进程、删除目录或自动产生功能 PASS。
IndependentEnvironment=NOT VERIFIED 与 CleanMachine=NOT TESTED 是脚本固定的取证边界；
环境身份和功能结果由测试人在本清单据实确认。

## 2. Portable 启动与实际路径

用资源管理器解压 ZIP 到 C:\Acceptance\测试 下载\MediaDownloader-Portable。
确认 MediaDownloader.exe、portable.flag、bin、_internal 存在，不直接在 ZIP 内运行。
双击 EXE，普通权限启动，打开 Runtime Health，保存状态/版本截图。

```powershell
.\clean_machine_test.ps1 -Stage portable-start -PortableRoot 'C:\Acceptance\测试 下载\MediaDownloader-Portable' -OutputDirectory 'C:\Acceptance\Reports'
```

保存 portable-runtime-health.json 和 clean-machine-report.json。
ModeMatches 必须 true，三个 PathsWithinRoot 必须 true，版本与 UI 相符。

| Runtime | 要记录的实际路径/位置 | Result | Evidence |
|---|---|---|---|
| Application | PortableRoot\MediaDownloader.exe | NOT TESTED | |
| FFmpeg | PortableRoot\bin\ffmpeg.exe | NOT TESTED | |
| FFprobe | PortableRoot\bin\ffprobe.exe | NOT TESTED | |
| QuickJS | PortableRoot\bin\runtime\qjs.exe | NOT TESTED | |
| Python | PortableRoot\_internal\python313.dll、python3.dll、base_library.zip | NOT TESTED | |
| Qt/PySide6 | PortableRoot\_internal\PySide6 下独立 DLL/plugins | NOT TESTED | |
| yt-dlp | MediaDownloader.exe 内嵌 PYZ package；Health 的 bundled Python package/version | NOT TESTED | |
| EJS | PortableRoot\_internal\yt_dlp_ejs\yt\solver\core.min.js、lib.min.js | NOT TESTED | |

yt-dlp 没有独立 yt-dlp.exe；PYZ member 不是独立文件系统路径。
脚本 EmbeddedYtDlp 字段是包位置说明，不是 archive-member 检验结果。
发行哈希锁定 B4.3 已审计 payload；独立环境仍需实测 Preview/Download，不得调用外部 Python。
在实际 Preview/Download 期间再次收集进程真实路径：

```powershell
.\clean_machine_test.ps1 -Stage portable-active -PortableRoot 'C:\Acceptance\测试 下载\MediaDownloader-Portable' -OutputDirectory 'C:\Acceptance\Reports'
```

检查 ObservedProcesses.ExecutablePath 与实际发行根目录相符。
快照可能错过短时 qjs/ffprobe；缺少快照不能虚构路径，保留 Health 实际工具路径/版本，必要时重复取证。
任务管理器 Details 的 Image path name 可补充证据。不得出现开发目录、系统 PATH 工具或开发 Python。
Windows 自带系统 DLL 不属于外部开发依赖。

## 3. Portable 功能与持久化

固定公开测试源视频 ID：E86EwGT_c2M（在 YouTube 打开），B4.3 曾验证真实 8K。
本阶段重新 Preview，不继承旧 PASS。源失效/网络不允许要记录原因；合法替换源须记录 ID、规格和替换理由。
不要保存带签名 token 的完整 formats URLs。
设置下载目的地 C:\Acceptance\Downloads\中文 下载 路径，使用新文件名避免旧文件跳过冒充完整下载。

| 按顺序执行 | Result | Evidence / 真实结果 |
|---|---|---|
| Launch | NOT TESTED | 普通权限窗口、无崩溃 |
| Runtime Health / bundled runtimes | NOT TESTED | READY、真实版本、完整路径 |
| Preview | NOT TESTED | 标题、真实 formats |
| 1080P 完整下载 | NOT TESTED | 完成状态、文件大小、视频+音频、时长 |
| 4K metadata / selection | NOT TESTED | 真实 2160P format 与选中状态 |
| 8K metadata / selection | NOT TESTED | 真实 7680×4320 format |
| Best Quality = 4320P | NOT TESTED | 8K 源自动选择；不得 upscale |
| Audio Only | NOT TESTED | 完整音频文件与 ffprobe |
| Cancel | NOT TESTED | 真实下载开始后取消、cancelled 状态 |
| Retry | NOT TESTED | Retry 真正启动并完成有效文件 |
| Chinese path | NOT TESTED | 中文目录中实际输出 |
| Space path | NOT TESTED | 带空格目录中实际输出 |
| Settings Save | NOT TESTED | 修改并保存目的地/设置 |
| Exit / Restart / Settings Persistence | NOT TESTED | 重启后设置相同 |
| History Persistence | NOT TESTED | 完成/取消记录保留，不意外重排队 |

用发行包内的 ffprobe 保存 1080P、Audio Only、Retry 结果；替换真实媒体文件名：

```powershell
& 'C:\Acceptance\测试 下载\MediaDownloader-Portable\bin\ffprobe.exe' -v error -show_streams -show_format -of json '实际完整媒体文件路径' | Set-Content 'C:\Acceptance\Reports\portable-1080p-ffprobe.json' -Encoding UTF8
```

1080P 必须真实 1920×1080、有音频、完整时长；只解析或下载片段不算完整下载 PASS。
4K/8K 此阶段要求 metadata/selection，不要求重下完整 8K。
记录重启前后值及历史。Portable 配置在 PortableRoot\config\app_settings.json，
历史在 PortableRoot\data\download_history.json。不将可能含敏感参数的整个配置/历史输出到公共日志。

## 4. Crash Recovery（Portable 或 Installer 至少一个）

1. 修改并保存 Settings，记录改动值。
2. 启动真实下载，确认 partial 文件或实际传输进度。
3. 在任务管理器强制结束本次 MediaDownloader，记录 PID、时刻、进度和是否连同 worker。
4. 重开同一 EXE：设置保留、历史可读、中断状态合理、Runtime Health READY。
5. 检查两个 JSON 可解析；替换当前包的实际文件路径，不打印配置内容：

```powershell
Get-Content -LiteralPath '实际 config\app_settings.json 路径' -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
Get-Content -LiteralPath '实际 data\download_history.json 路径' -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
```

保存解析、重启和 Health 证据。强杀空闲窗口或 fixture 单元测试不算本项 PASS。
若异常结束留下 worker，记录原因；事后强杀 worker 不算正常退出无残留 PASS。

| Crash Recovery item | Result | Evidence |
|---|---|---|
| Active transfer before forced exit | NOT TESTED | |
| Settings readable / retained | NOT TESTED | |
| History readable / interruption recovered | NOT TESTED | |
| JSON not corrupted | NOT TESTED | |
| Runtime Health after restart | NOT TESTED | |

## 5. Portable 整目录删除

1. 正常关闭应用，确认任务管理器无本次 MediaDownloader.exe、ffmpeg.exe、ffprobe.exe、qjs.exe 残留。
2. **不传 PortableRoot**，避免检查脚本启动诊断进程；收集退出后快照：

```powershell
.\clean_machine_test.ps1 -Stage portable-exit -OutputDirectory 'C:\Acceptance\Reports'
```

3. 资源管理器删除整个 C:\Acceptance\测试 下载\MediaDownloader-Portable，确认无锁定/部分删除。
4. 检查目录不存在，截图并收集删除后快照：

```powershell
Test-Path -LiteralPath 'C:\Acceptance\测试 下载\MediaDownloader-Portable'
.\clean_machine_test.ps1 -Stage portable-deleted -OutputDirectory 'C:\Acceptance\Reports'
```

Test-Path=False，加真实删除与无残留证据，才能 Portable Delete=PASS。
旧自动化 blocked by policy 只属旧环境限制；本次删除失败记录实际原因。
必须在 Sandbox 自动销毁前手动完成，自动销毁不代替删除测试。

| Item | Result | Evidence |
|---|---|---|
| Normal exit / zero app/native processes | NOT TESTED | |
| Entire Portable directory deleted | NOT TESTED | |

## 6. Installer 安装与正常运行

1. 双击 Setup，记录安装位置/权限选择，验证开始菜单及选中的桌面快捷方式。
2. 快捷方式普通启动；安装可以按设计请求权限，正常运行不得要求 Run as Administrator。
   记录运行提权提示情况，任务管理器 Details 的 Elevated 列可作辅助证据。
3. Runtime Health、Preview、完整 1080P，保存到安装目录外 C:\Acceptance\Downloads\Installer 中文 spaces。
4. 用实际安装根收集诊断/进程路径：

```powershell
.\clean_machine_test.ps1 -Stage installer-active -InstallerRoot '实际安装目录' -OutputDirectory 'C:\Acceptance\Reports'
```

5. ModeMatches=true；FFmpeg/FFprobe/QuickJS 全在安装根；Python/Qt/EJS 对应第 2 节文件。
6. 使用安装目录内 ffprobe 检查实际完整视频+音频/分辨率/时长。
7. 修改保存 Settings，退出、重启，验证设置/历史持久化。
   默认配置/历史在 %LOCALAPPDATA%\MediaDownloader\config\app_settings.json
   和 %LOCALAPPDATA%\MediaDownloader\data\download_history.json。
8. 尚未完成 Crash Recovery 时按第 4 节执行。

| Installer item | Result | Evidence |
|---|---|---|
| Install / Start Menu / chosen desktop shortcut | NOT TESTED | |
| Launch without required elevation | NOT TESTED | |
| Runtime Health / Runtime Isolation | NOT TESTED | |
| Preview | NOT TESTED | |
| 1080P complete video + audio | NOT TESTED | |
| Settings Save / Restart / Settings Persistence | NOT TESTED | |
| History Persistence | NOT TESTED | |

## 7. 标准卸载

1. 关闭应用。记录下载视频路径、大小、SHA256，以及原安装目录/快捷方式/卸载项存在的证据。
2. Windows Installed Apps 标准卸载。
3. 验证安装目录、开始菜单快捷方式、所选桌面快捷方式、卸载项全部删除。
   Inno AppId：{97D1CD48-54D0-4951-A662-9C62AA1A789B}；卸载 registry 子键带 _is1。
   按安装范围检查 HKCU/HKLM（包括必要的 WOW6432Node），不修改 registry。
4. 下载视频仍存在，大小/SHA256 与卸载前一致。
5. 当前策略保留配置，记录 User configuration intentionally preserved。
6. 不传 InstallerRoot，收集卸载后快照：

```powershell
.\clean_machine_test.ps1 -Stage installer-uninstalled -OutputDirectory 'C:\Acceptance\Reports'
```

| Uninstall item | Result | Evidence |
|---|---|---|
| Program files removed | NOT TESTED | |
| Start Menu / chosen desktop shortcuts removed | NOT TESTED | |
| Uninstall entry removed | NOT TESTED | |
| Download files preserved (size/hash unchanged) | NOT TESTED | |
| Configuration intentionally preserved | NOT TESTED | |
| No remaining app/native processes | NOT TESTED | |

## 8. 最终判定与证据导出

各表按实际结果填写 PASS / FAIL / NOT TESTED，附对应证据。
证据包：环境来源说明、preflight、各阶段 JSON/MD、Health、UI/路径/进程截图、媒体 ffprobe、
持久化/Crash Recovery、目录删除、卸载与下载文件保留。Sandbox 关闭前导出证据。
不要记录/上传 Cookie 值、Authorization、完整敏感 token 或浏览器数据库。

全部必需项实际 PASS，特别是 Portable Launch/Isolation/1080P/Persistence/Delete，
Installer Install/Launch/Isolation/1080P/Persistence/Uninstall 与 Crash Recovery，才能：

```text
Clean Machine Gate: PASS
Public Distribution Gate: NEEDS LEGAL REVIEW (unchanged)
```

无独立环境、未执行或证据缺失，保持 Clean Machine Gate=NOT TESTED；
真实产品运行失败记录 FAIL。网络/策略/环境阻碍单列原因，不推测 PASS。
完成后停止，不进入 B5，不发布 v1.0，不开展法律判断。
