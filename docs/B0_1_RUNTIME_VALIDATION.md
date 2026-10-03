# B0.1 Runtime Validation & Core Reliability

**Result: CONDITIONAL PASS。真实 SDR AV1 8K = PASS。** 1080P/4K/audio、resume、实际代理转发、受控cookie认证、各阶段取消、成功/失败状态通过。真实浏览器账号认证尚未验收，不能给整体PASS。开放条件见 `B0_1_FIXES.md` O1–O7。此阶段结束，不进入B1/B2。

## 环境与Git边界

- 日期：2026-10-01，Windows11 Pro 10.0.26200 AMD64；Python3.13.13、yt-dlp2026.8.19、PySide6 6.11.2、PyYAML6.0.3；PATH FFmpeg/ffprobe8.0 Gyan。
- 开始时 `git status`干净，`git branch`/`git rev-parse HEAD`已检查；从655bcb1923d412cc7737f6bcd3b3ee220546b089创建`codex/b0-1-core-runtime-validation`。
- master保留0e42112dae627c10ce159ece0ef97594ccd27d39；codex/b0-source-audit保留655bcb1923d412cc7737f6bcd3b3ee220546b089。B0报告不修改。
- 修复只涉及option流、类型/PP、preset、安全、状态与可终止worker。原ThreadPoolExecutor调度和yt-dlp下载逻辑保留；没有UI美化、新平台、DB、代理池、账号系统、新依赖。

## 核心复现与修复依据

基线GUI预览调用manager时不传collect_opts，实际下载另建options，故预览缺代理/认证。基线preset稀疏dict整体apply_settings导致缺项回默认，原YAML retry_sleep_functions.http=3而API需要callable；大小filter为string，日期/match_filter/metadata/SponsorBlock映射不符合实际API。原password/proxy userinfo可进入配置，线程cancel等下次hook才生效，私有retcode补丁和progress不能证明最终输出。对应最小修复、文件和测试见FIXES，具体调用链见OPTION_FLOW。未以这些源码结论冒充修复前的实网捕包。

## Proxy / Cookies

`tests/validate_network.py`使用本机HTTP CONNECT和SOCKS5 authenticated forwarder，向公开YouTube请求真实metadata和完整audio；不是mock网络。endpoint验证host127.0.0.1、随机port和dummy username/password正确握手；日志仅记录验证布尔值与计数。Preview与Download使用同一options snapshot。

最终复跑记录在`D:\YouTube视频下载\B01 evidence\network-final-2\network-results.json`。HTTP/SOCKS5/SOCKS5H均preview有请求、download有请求及CDN访问、completed、非空output、active_children0。两种SOCKS在当前依赖都使用domain ATYP3，不据此宣称不同DNS解析行为。无代理实际YouTube Preview成功，effective proxy为明确直连空字符串；format=ba，timeout15.0，retries1，extractor_retries1，continuedlTrue，cacheFalse，http retry delay callable3秒。

| 真实代理测试 | host / port | Preview requests | Download requests | Auth / CDN / same options |
|---|---|---|---|---|
| HTTP | 127.0.0.1 / 10431 | 3 | 4 | True / True / True |
| SOCKS5 | 127.0.0.1 / 10480 | 3 | 4 | True / True / True |
| SOCKS5H | 127.0.0.1 / 8066 | 3 | 4 | True / True / True |

Cookie文件测试使用受控Netscape cookie和本地拒绝未认证请求的真实HTTP媒体服务。两阶段都cookie_ok=True、User-Agent一致，完整下载completed；没有输出Cookie内容。Chrome/Edge/Firefox是原有UI和yt-dlp支持，tuple映射通过；未访问个人profile，真实浏览器解密/登录为NOT TESTED。没有用户提供账号/代理配置时采用受控环境，不将其等同YouTube登录态实测。

## Completed / Failure / Cancel / 进程

- completed在真实yt-dlp returncode0、after_move最终文件存在且>0、postprocess结束、子进程成功退出且未取消后产生。保留原状态字符串canceled，即cancelled语义。
- Cookie服务HTTP500确定失败→failed；缺失FFmpeg路径→failed/无最终output。真实video394+audio251下载后给merger注入非法参数：merger_startedTrue、failed、final_outputs空、worker_children0。不是仅缺路径的替代验证。
- 8K video下载61190074/611459589 bytes时cancel，.part稳定，child0；audio下载64512/2524258 bytes时cancel，同样稳定。
- active merge实见Windows ffmpeg PID21836，cancel后PID消失，child0；立即重新同URL能完整下载合并。另一次阶段测试也观察PID15896终止。
- Resume视频首次进度61191098 bytes而非0；4K恢复首次71730928 bytes。实际PART恢复，不只检查continuedl选项。
- Success/failure/cancel/GUIexit均检查multiprocessing child回收；Windows tasklist/CIM核对FFmpeg PID。没有永久本任务yt-dlp/ffmpeg/ffprobe/python child。系统无关Python进程不作为残留，也不终止它。

## GUI响应

真实MainWindow/QApplication，QTimer20ms，脚本移动窗口、打开Settings、Preview、下载、FFmpeg remux、Cancel All、close。最终ticks：preview74、download81、postprocess300、cancel22、exit1；最大间隔0.037654秒；耗时9.829483秒；completedTrue、cancelledTrue、exit后child0。证明基本event loop响应，未声称人工主观拖动体验或GPU播放性能。代理实网测试走相同worker路径，但专门“GUI代理期间计时”NOT TESTED。

## 真实8K证据

来源：[Xiaomi 11T Pro 5G 8K Sample Video](https://www.youtube.com/watch?v=E86EwGT_c2M)，metadata duration155秒。先查全部formats：另一个标题写8K的候选iTx7_9AxipY当时没有4320格式，被排除。最终用源真实格式，不依标题/文件名判断。

| 字段 | 视频 | 音频 |
|---|---|---|
| format_id | 571 | 251 |
| width / height | 7680 / 4320 | null / null |
| fps | 30（metadata约数） | null |
| vcodec / acodec | av01.0.16M.08 / none | none / opus |
| dynamic_range | SDR | null |
| tbr / vbr kbps | 31613.865 / 31613.865 | 130.468 / 0 |
| ext | mp4 | webm |
| filesize / filesize_approx bytes | 611459589 / 611459569 | 2524258 / 2524245 |

默认`bv+ba`、无自定义sort、无固定上限，实际选择571+251（native best audio，不固定MP4/AAC）。完成两条完整流下载、FFmpeg merge；最终通过已有显式remux_video=mp4无损copy封装。没有scale、upscale、视频recode或fps转换。

最终文件：`D:\YouTube视频下载\B01 evidence\8k-native\native8k_E86EwGT_c2M.mp4`，614031948 bytes，container=`mov,mp4,m4a,3gp,3g2,mj2`，duration154.781000秒。SHA256：`E623C4A288639EE854556FF152E838D0AC70A037653DA575AD2C34681FF6C475`。

| ffprobe字段 | 视频 | 音频 |
|---|---|---|
| codec_name / codec_long_name | av1 / Alliance for Open Media AV1 | opus / Opus (Opus Interactive Audio Codec) |
| width / height / pix_fmt | 7680 / 4320 / yuv420p | null / null / null |
| r_frame_rate / avg_frame_rate | 30000/1001 / 1158750/38683 | 0/0 / 0/0 |
| bit_rate bits/sec | 31611263 | 127631 |
| duration秒 | 154.732000 | 154.781000 |
| color_transfer / color_primaries | bt709 / bt709 | null / null |

metadata30不意味着恒定30；copy保留源VFR timestamps。最终完整解码命令（无-t、无片段裁剪）：

```powershell
ffmpeg -v error -stats_period 10 -progress pipe:1 -i "D:\YouTube视频下载\B01 evidence\8k-native\native8k_E86EwGT_c2M.mp4" -fps_mode passthrough -enc_time_base:v demux -f null -
```

退出码0，stderr文件0 bytes，progress=end；`final-8k-result.json`、`final-ffprobe.json`、`final-decode-progress.log`、`final-decode-errors.log`保存在8k-native目录。null sink采用源timebase只为避免验收器VFR时间舍入；没有改变下载文件。完整AV1软件解码低于实时速度不影响文件有效结论，未验收硬件流畅播放。

**8K PASS范围：这个155秒SDR AV1真实源、完整音轨、无损MP4最终文件。** 默认MKV的FFmpeg8 Opus警告、先前null sink DTS诊断仍保留记录；不能扩大为所有容器/编码/HDR/60FPS全通过。`hVvEISFw9w0`实际formats中702=7680×4320、60fps、AV1 10bit HDR10，仅metadata识别；8K60/HDR完整下载及色彩保真NOT TESTED，不阻塞普通8K本次结论。

## 回归与复现

1080P/4K使用[Big Buck Bunny](https://www.youtube.com/watch?v=aqz-KE-bpKQ)，完整视频634秒级，非节选下载；399+140=1080P60、401+140=4K60，AV1+AAC。audio140经FFmpegExtractAudio输出MP3约634.62458秒。这些回归显式sort选择AAC，不声称当前GUI默认best audio是140；native8K默认确实为251。三个回归解码抽查10秒并ffprobe，8K全片解码；详见REGRESSION。

可在repo `.venv`运行：

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tests\validate_network.py "..\B01 evidence\network-recheck"
.venv\Scripts\python.exe tests\validate_gui.py "..\B01 evidence\gui-recheck"
.venv\Scripts\python.exe tests\validate_failure.py "..\B01 evidence\failure-recheck"
.venv\Scripts\python.exe tests\validate_media.py "..\B01 evidence\8k-recheck"
```

live tests有网络/磁盘成本，8K会下载约614MB并全片软件解码；需要FFmpeg/ffprobe。原始媒体、Cookie fixture、含短期签名URL的metadata和日志放repo外，不提交。测试代码仅含dummy本地认证。报告包含来源ID和脱敏结果便于复核，不包含敏感token。
