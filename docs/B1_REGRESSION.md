# B1 Regression

2026-10-02。**B1 Result: PASS（按本阶段架构及已执行回归范围，可进入B2；本次仍停在B1）。** 无确认的新P0、阻塞B2的P1；现有10项+新增6项=16项自动测试PASS。Known P2/P3及未测能力不因本结果变成已验证。

## 回归矩阵

| Test | Status | Actual Evidence / Limits |
|---|---|---|
| Application Launch | PASS | 真实MainWindow/QApplication显示并关闭；main入口编译通过 |
| Preview | PASS | GUI公开YouTube/本地认证媒体和proxy各Preview，非GUI阻塞IO |
| 1080P | PASS | GUI完整E86EwGT_c2M：399视频+251音频；ffprobe1920×1080 AV1/Opus，MP4 |
| 4K | PASS | GUI完整401+251；ffprobe3840×2160 AV1/Opus，MP4；Cancel后Retry恢复 |
| 8K Metadata | PASS | 默认bv+ba实际571=7680×4320 fps30 AV1 SDR +251 Opus；无height cap |
| 8K Full Regression | PASS | 因hook/model影响核心额外完整下载；611459589-byte video+2524258-byte audio；合并、copy remuxMP4；最终614031948bytes，154.781秒；全片decode退出0/stderr0 |
| Audio | PASS | GUI251 Opus→FFmpegExtractAudio→MP3，最终ffprobe音频mp3 |
| Resume | PASS | GUI4K Retry第一条download progress32853203bytes非0；8K.part恢复另记录 |
| Cancel | PASS | GUI4K10%取消、Cancel All、exit；8Kvideo/audio/真实activeFFmpeg取消，part稳定 |
| Retry | PASS | GUI真实旧行Retry→新ID→4K完整成功；manager拒绝active retry/newduplicate |
| Completed | PASS | 只有原生return0+after_move非空final+child0+未取消才completed；模型终态保护 |
| Failed | PASS | 真实HTTP500、缺FFmpeg、实际merger非法参数失败；状态failed、无final、child0 |
| cookies.txt | PASS | Cookie-gated本地真实认证服务；两个阶段cookie_ok/User-Agent一致；GUI完整媒体 |
| HTTP Proxy | PASS | loopback authenticated真实YouTube；GUI完整audio，network preview3/download4，CDNTrue |
| SOCKS5 | PASS | GUI完整audio、真实forwarder；network preview3/download4，认证True |
| SOCKS5H | PASS | GUI完整audio、network preview3/download4，认证True；不声称与SOCKS5不同DNS语义 |
| Queue | PASS | 新模型queued、active去重、remove/cancel、terminal retry、新ID；worker并发配置单元验证 |
| Duplicate Task Protection | PASS | 锁内按URL拒绝全部非terminal（含postprocessing）；真实取消后可再开 |
| History | PASS | 白名单序列化、旧状态归一化、读取深拷贝、quality/output/error字段、clear；GUI7条final records |
| Settings | PASS | 统一store/typed projection、受保护长期字段、原GUIpreset switching、下载/分片并发独立 |
| Logs | PASS | 四等级、proxy/header秘密mask、1MiB/3backup rotation配置；GUI queued Signal、2000block/close detach |
| Existing automatic tests | PASS | 原10项保留测试语义；状态/IPC/旧mock适配规范接口，不删失败测试 |
| New automatic tests | PASS | 6项：状态与未来>8K模型、settings/preset、cookie/proxy、history、queue/events/retry、rotating日志 |
| Compile / Diff | PASS | compileall及git diff --check |
| Browser authentication | PARTIAL | Chrome/Edge外部读取失败；Firefox此次Preview遇到一次bot confirmation、Download成功；未改成登录PASS |
| Playlist全列表专项 | NOT TESTED | 原生参数和合法多entry state cycle保留；未完整下载大型playlist |
| 8K60/HDR完整专项 | NOT TESTED | B2及独立媒体验证范围；本次SDR AV1全片通过 |
| Frozen packaging | NOT TESTED | freeze_support保留，非本阶段打包任务 |

## 实际运行数据

GUI七项实网烟测`tests/validate_b1_desktop.py`：1080P、4Kcancel/retry、MP3、Cookiefile、HTTP、SOCKS5、SOCKS5H全部Preview+Download通过；最大20ms QTimer间隔0.3692595秒，7条history，exit child0。

最后的GUI处理/exit专测`tests/validate_gui.py`：ticks Preview74/Download85/PP297/Cancel25/Exit1，max_gap0.0346094秒，completedTrue/cancelledTrue，exit child0。测试代码timer监视任务并不意味着产品UI轮询。

8K三阶段cancel记录包含真实ffmpeg PID19500，cancel后已移除。Windows最终CIM检查无ffmpeg/ffprobe/本次python children，仅无关原有python PID4180存在，不终止它。保留yt-dlp合并，explicit remux_video=mp4只copy；全片decode null sink用passthrough+demux时间基准，无-t、无scale/fps转换。

实际FFmpeg失败：394视频和251音频已下载、merger_startedTrue，native option not found→failed/final_outputs空/children0。未将100%progress当完成。

原10tests仍10项，新增6项，总16。状态测试从旧RUNNING→COMPLETED断言改成8值协议的正常序列；旧mock文件验证适配、错误IPC dict字段和canonical cancelled拼写迁移是接口更新，不是删掉断言。live tests也相同语义保留。未重新定义历史B0/B0.1/B0.2结果。

## Evidence

repo外`D:\YouTube视频下载\B1 evidence`：

- `desktop/desktop-results.json`、`desktop/desktop-summary.json`及实际媒体/history/settings
- `gui-final/gui-results.json`
- `network/network-results.json`（HTTPport6599/SOCKS5port10491/SOCKS5Hport9788）
- `failure/failure-result.json`
- `8k/media-results.json`、`8k/ffprobe.json`、`8k/decode-progress.log`、`8k/decode-errors.log`及完整MP4
- `auth/auth-flow-results.json`保留浏览器外部失败/Firefoxbot提示；非file认证失败
- 外层`B1-unit.log/B1-desktop.log/B1-gui-final.log/B1-network.log/B1-failure.log/B1-8k.log/B1-auth.log`

原始签名URL不dump、不提交Cookie文件/内容、媒体或日志。本机运行可复核以下显式脚本：

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tests\validate_b1_desktop.py "..\B1 evidence\desktop-recheck"
.venv\Scripts\python.exe tests\validate_gui.py "..\B1 evidence\gui-recheck"
.venv\Scripts\python.exe tests\validate_network.py "..\B1 evidence\network-recheck"
.venv\Scripts\python.exe tests\validate_media.py "..\B1 evidence\8k-recheck"
```

8K会下载约614MB并全片软件解码；重跑cancel/resume脚本使用新目录，不把缓存命中当下载。另有B0.2 live浏览器脚本，仅显式运行时读取profile。没有额外软件安装或全依赖升级。

## Still Open / Severity / Impact on B2

| ID | Severity | Open | Impact on B2 |
|---|---|---|---|
| O1 | P2 Medium | 原生YouTube extraction警告无启用JS runtime，可能缺某些formats；当前8K正常 | 不阻塞接口开发；广泛格式排序验收前应配置官方支持runtime再查formats |
| O2 | P2 Medium | 默认MKV/Opus在本机FFmpeg8有历史probe诊断，explicit MP4 copy全片通过 | B2容器兼容策略需验证，不能自动recode/upscale |
| O3 | P2 Medium | Chrome/Edge锁/DPAPI与Firefox未登录/bot提示；file正式路径通过 | 按已修订Auth Product Policy不阻塞B2，错误与fallback清楚保留 |
| O4 | P2 Medium | JSON持久化仍非atomic；高级功能Defer、部分typed字段预留、大型playlist展开/全专项未测 | 不阻塞B2；交付前收尾store/产品范围及playlist证据 |
| O5 | P3 Low | 项目3.0.0/About3.1原标识差异 | 不阻塞B2，本阶段不品牌化 |

确认新P0=0、阻塞B2的P1=0、剩余P2问题组4、P3问题组1。B1完成后停止；不实现完整Format Selector、HDR/8K UI或新增平台。
