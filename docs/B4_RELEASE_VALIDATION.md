# B4 Release Validation

Date: 2026-10-02. Branch: codex/b4-runtime-packaging. Base: B3 11b723a1daeb6dc82e3705c2955f8beb2cddc984.
**B4 Result = CONDITIONAL PASS**。本机源码、Portable、Installer 与核心运行回归通过；
不能标为 PASS，干净 Windows 环境验收和完整公开转发行审查尚未完成。
没有进入 B5、发布 v1.0 或新增平台。

## Environment / evidence

Windows 11 Pro 10.0.26200，AMD64，普通用户。Legacy WindowsProductName 标签返回 Windows 10，
实际 OsName/平台为 Windows 11，因此没有把本机误记为 Windows 10 PASS。
目标 EXE PATH=`C:\WINDOWS\System32;C:\WINDOWS`；清除 Python/Qt plugin 环境覆盖。
测试父进程的 Python/loopback server 是 fixture，不被目标程序用于运行/下载。

主要证据根目录：`D:\YouTube视频下载\B4 evidence`。

| Evidence | Content |
|---|---|
| portable-runtime/results.json, summary.json, host-fixtures.json | 10 frozen GUI cases，工具路径、状态、proxy/auth counts |
| installed-runtime/同名文件 | 10 installed frozen GUI cases |
| portable-lifecycle/lifecycle.json | restart、idle force-kill、long path、missing Deno |
| installed-lifecycle-retest/lifecycle.json | 相同 installed 检查 |
| final-portable/results.json、final-installed/results.json | 最终 notice 修订后的 ZIP/Setup，fresh 1080 + 8K metadata |
| final-artifact-equivalence.json | 最终 EXE 内嵌 archive 每个 member 和全部 native bin 与 full-suite build 相同 |
| installer-metadata.json / uninstall.json | 两次安装、可选桌面 shortcut、真实卸载与数据保留 |
| check-update.json | 官方版本只读检测，未替换文件 |
| defender-scan.json | 本地 Defender custom scan completion |
| portable-runtime/*-ffprobe.json | 完成输出的真实媒体结构 |
| portable-runtime/8k-decode-* | 新 8K 全片 decode |

最后 rebuild 只修正 NOTICE 的转发行边界说明。EXE PE hash 因构建时间不同；逐个 archive member
及 native bin 字节等价检查 PASS。最终两个 artifact 另做 fresh 1080P 下载、8K Preview。
没有把 notices-only rebuild 未重复的整个 suite 冒充为第三次 full-suite execution。

## Runtime / launch

| Item | Source | Portable | Installer |
|---|---|---|---|
| build / launch | PASS | PASS | PASS，install/uninstall exit 0 |
| yt-dlp | 2026.8.19 | 同版本 bundled package READY | 同版本 bundled package READY |
| FFmpeg / FFprobe | bundled n8.1.3-14-g330caae0c1-20261001 | bin 下绝对路径 READY | 安装目录 bin 下绝对路径 READY |
| JS | Deno 2.9.7 + EJS 0.8.0 | bin/runtime/deno.exe READY | 同上 READY |
| writable config/download/temp | PASS | READY | READY，用户数据在 LOCALAPPDATA |
| Runtime Isolation | source 可 fallback | Windows-only PATH PASS | Windows-only PATH PASS |
| no Deno | 同源 preview/download PASS | physical hide，launch/Preview PASS | 相同 PASS |
| Clean Machine | 不适用 | NOT TESTED | NOT TESTED |

没有现成 Windows Sandbox/独立 VM；用户选择推荐的 NOT TESTED 路径。
PATH 隔离不能证明独立机器不存在其他 DLL/运行库帮助；干净环境验收仍为 P1 release gate。
Windows 10 / 中文 Windows 用户名 / all-users Program Files install = NOT TESTED。

## Real frozen regression

同一真实公开视频 E86EwGT_c2M，source quality ranking 保持 B2；当前最高有效 4320P，
没有 2160/4320 写死上限。源有音视频的流精确 ID 组合，最高模式不转码。

| Check | Portable | Installer | Notes |
|---|---|---|---|
| Preview / Analyze | PASS | PASS | 同一 Manager/options，实际 formats |
| 1080P | PASS，full 399+251 | PASS，full 399+251 | 最终 artifact 又各下载新的 1080 文件 |
| 4K | PASS，full 401+251 | metadata PASS | 新文件 3840×2160，AV1 + Opus，154.774s，324633315 bytes |
| 8K metadata / Best | PASS，571+251 | PASS | 4320P；真实 labels/selection/task，非 synthetic |
| 8K full download / merge / probe / decode | PASS | 不重复 full download | 详见下一节 |
| Audio Only | PASS，MP3 extraction | PASS，MP3 extraction | bundled FFmpeg |
| Resume / Retry | PASS，4K cancel -> fresh retry | 旧行为和 unit regression PASS | first bytes=1024，retry first bytes=2097152；新任务完成 |
| Cancel | PASS，1080 cancelled | PASS，1080 cancelled | .part 保留用于重试 |
| Active download exit | PASS | PASS | warning 分支、Yes、cancel；shutdown children=0 |
| Queue / events | PASS | PASS | real records/status/progress + 105 旧 unit/integration tests |
| History | PASS，重启前后 11 条保持 | PASS，重启前后 8 条保持 | lifecycle 后增加 long-path 条目，未自动排队 |
| Settings | PASS | PASS | GUI Save retries=7、workers=1、path；restart 保持 |
| idle crash / restart | PASS | PASS | 两次真实强杀空闲主窗口，JSON 可读、history terminal |
| Logs | PASS | PASS | 1 MiB x 1 current + 3 backups，SafeFormatter，UI日志原链路保留 |
| cookies.txt | PASS | PASS | controlled Cookie-required server；Preview+Download 均 authenticated |
| HTTP Proxy | PASS | PASS | authenticated forwarding，7 request records each |
| SOCKS5 | PASS | PASS | 同上 |
| SOCKS5H | PASS | PASS | 同上 |
| Chinese / space path | PASS | PASS | EXE、安装、媒体目标均含中文/空格 |
| Long path | PASS | PASS | 实际输出路径 216 字符，完整 12s 1280×720/AAC fixture |
| Uninstall | 不适用 | PASS | 程序/shortcuts/key 删除；settings/download 保留 |
| Portable folder delete | NOT TESTED | 不适用 | 自动审批拒绝递归删除，blocked by policy；副本保留 |

fixture HTTP Cookie 和 proxy 密码仅是本地测试值，不是个人 YouTube 账号凭据；不记录 Cookie 内容。
两种模式请求证据 cookie_authenticated=true、三种 proxy_auth=true；Runtime Health 绝对路径
证实工具来自发行目录。扫描应用 logs/config，无 controlled Cookie value 或 proxy password。
B0.2 的真实账号/浏览器历史结果不被改写，Chrome/Edge 仍 EXPERIMENTAL。

UI 全页切换/移动时 25ms 定时器实际运行，full suite 最大间隔 Portable=0.068353s、Installed=0.072769s。
这是 acceptance harness 测量，不是专业性能基准。启动首次观察/暖启动分别
Portable=0.524/0.542s、Installed=1.167/0.957s。OS 冷缓存启动 NOT TESTED，不能把这些数称为真实冷缓存测试。

## New complete 8K evidence

Output: `D:\下载测试\YouTube视频\B4下载验证\portable-8k_E86EwGT_c2M.mp4`。
完成状态、输出存在、分离 video/audio stream 下载、bundled FFmpeg merge 全部 PASS。

| Property | Actual |
|---|---|
| selection | 571+251 |
| video | AV1，7680×4320，yuv420p，avg_frame_rate=5991/200 |
| audio | Opus，独立 audio stream 存在 |
| duration | 154.774000 s |
| container | MP4，ffprobe format_name=mov,mp4,m4a,3gp,3g2,mj2 |
| size | 614003521 bytes |
| SHA256 | 6081e098cec1af01b321720ed8185cbf6c312559ff700ab1a432094d39bd4325 |
| full decode | exitcode=0，errors_bytes=0，4635 frames，progress=end，dup/drop=0 |

使用该 Portable 自带的 FFmpeg，`-v error -xerror -threads 4 -map 0:v:0 -map 0:a:0
-fps_mode passthrough -enc_time_base:v demux -f null -`，没有 -t/片段采样或 upscale。
视频全片最终 progress=154.732098s，音视频 container duration=154.774s。
8K PASS 来自完整文件/音视频/分辨率/全片解码，不只是 format_id 或 metadata。

## Tests / resolved failures

`D:\YouTube视频下载\B4-final-tests.log`：135 tests，10.060s，OK。
Previous=105 PASS；New=30 PASS；Total=135 PASS；无 skip。
新增覆盖 17 个要求及同目录原子替换、异常保旧值、backup/schema/Unicode、安全持久化。
辅助真实 validation scripts 不计入 30 个 unittest 数量。

Qt 初次 frozen 导入失败已定位/修复，详见 packaging report。JS stdin harness 初次失败和
长路径 fixture 初次尾随空格错误保留失败日志，修正 driver 后 retest PASS。
既有 protected branch refs：master=0e42112dae627c10ce159ece0ef97594ccd27d39，
B1=744de1ecc0ecfa233f36a189f91959b2dd43f46e，B2=ec9c2950ecdb487455dd090470835ce95650e51e，
B3=11b723a1daeb6dc82e3705c2955f8beb2cddc984；仅 B4 提交变更。

## Release disposition

| Severity | Count | Still open / release impact |
|---|---:|---|
| P0 | 0 | 无已发现核心失败 |
| P1 | 2 | ① Portable/Installer clean-machine 未验收；② 完整第三方 notices/对应源码安排未复核。阻止无条件 RC/公开发布 PASS |
| P2 | 2 | YouTube 上游挑战/Chrome-Edge 直接读取限制；旧播放器 AV1/VP9/Opus 兼容性。已提供认证/画质提示策略，不阻止本机核心 PASS |
| P3 | 2 | 全面语言切换仍部分覆盖；Portable 实际删除测试被自动审批阻止。保持未完成，不虚构 PASS |

Windows 10/中文用户名/OS cold-cache/all-users install 为可选环境覆盖 NOT TESTED。
JSON atomic-save 原 P2 已解决；JS 集成已验证，来源可用性风险仍在；播放器提示策略完成，
没有因为播放器兼容性降分辨率/FPS、重新压缩或 upscale。
Defender custom scan 2026-10-02 11:36:02 完成（15s），Get-MpThreatDetection 无条目；未上传任何文件。
产物 sizes/digests 见 B4_PACKAGING 和 dist/release/checksums.txt。
完成 B4 本地交付后停止；独立环境验收/转发行审查未被推定完成。
