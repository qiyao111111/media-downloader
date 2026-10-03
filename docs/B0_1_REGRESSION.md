# B0.1 回归矩阵

2026-10-01；状态仅使用PASS/FAIL/PARTIAL/NOT IMPLEMENTED/NOT TESTED。总体CONDITIONAL PASS，详情及开放条件见RUNTIME_VALIDATION/FIXES。

| Test | Status | 实际证据 / 结论边界 |
|---|---|---|
| 1080P | PASS | 完整399视频+140音频；1920×1080、60fps、AV1/AAC、MP4；ffprobe含两流，10秒decode退出0/errors0 |
| 4K | PASS | 完整401视频+140音频；3840×2160、60fps、AV1/AAC、MKV；ffprobe两流，10秒decode0/errors0；不能当全片decode验收 |
| 8K | PASS | native默认571+251完整download/merge，显式copy remuxMP4；7680×4320 AV1/Opus SDR、614031948bytes、154.781秒、全片decode0/stderr0 |
| 8K60 metadata | PASS | source hVvEISFw9w0 format702、7680×4320 fps60 AV110bit HDR10真实识别 |
| 8K60完整下载 | NOT TESTED | metadata不等于下载PASS |
| 8K HDR完整下载/色彩验证 | NOT TESTED | 未验收最终HDR pix_fmt/transfer；普通SDR8K通过 |
| 8K VP9 / AVC其他编码 | NOT TESTED | 不扩大AV1成功结论 |
| 1440P完整专项 | NOT TESTED | 架构无上限，但本阶段未独立下载验收 |
| Audio MP3 | PASS | source140 AAC→FFmpegExtractAudio→MP3，634.62458秒；ffprobe音频，10秒decode0/errors0 |
| Audio FLAC | NOT TESTED | preset已存在、ba已修正；未做实际输出验收 |
| 4K Resume | PASS | cancel10%，restart首进度71730928bytes，完整合并输出 |
| 8K Resume / Restart | PASS | video取消61190074bytes，恢复first61191098bytes；audio/merge取消后同URL可重新完成 |
| No Proxy Preview | PASS | 公开YouTube真实metadata，effective proxy=''（direct），formatba |
| HTTP Proxy Preview / Download | PASS | loopback authenticated CONNECT真转发Internet；两阶段请求计数、凭据验证True、CDN访问与完整audio |
| SOCKS5 / SOCKS5H Preview / Download | PASS | loopback真转发Internet、host/port/username/password握手、完整audio、child0；两者当前ATYP3，不承诺不同DNS语义 |
| HTTPS Proxy backend | NOT TESTED | 不等同HTTP CONNECT到HTTPS目的地址；额外backend未装 |
| Cookiefile Preview / Download | PASS | 受控Cookie-gated真实服务，两阶段认证True、User-Agent一致，完整download；未当YouTube账号实测 |
| Chrome / Edge / Firefox option mapping | PASS | 原功能string→tuple；真实API路径保留 |
| Chrome / Edge / Firefox真实登录 | NOT TESTED | 无授权测试profile/账号，不读取个人Cookie |
| Cookies总体 | PARTIAL | 文件认证PASS，真实浏览器/YouTube登录缺证据 |
| username/password/netrc真实认证 | NOT TESTED | 参数链和会话安全测过；没假称账号成功 |
| extractor_args / impersonation行为 | NOT TESTED | 非GUI现有控件；不删除API参数；未做特殊backend/extractor实网验收 |
| Cancel video10% / audio / activeFFmpeg | PASS | 8K三阶段实测，part稳定，Windows ffmpeg PID21836终止，child0 |
| Cancel All / Application Exit | PASS | 实际GUI worker下载取消、预览exit取消，child0 |
| Completed State | PASS | returncode0+after_move输出>0+PP完成+child成功+未取消；不是progress100% |
| Download Failure State | PASS | 本地HTTP500真实异常→failed，child0 |
| FFmpeg Failure State | PASS | 两流下载结束、真实merger_started、非法FFmpeg参数→failed、无最终output、child0 |
| Preset Switching | PASS | GUIproxy/cookies/path/template/FFmpeg/subtitles保留；audio→video不会残留extract_audio |
| Credentials / Masking | PASS | dummy秘密不在settings/presets/日志；legacy settings清理；Cookie路径保留，内容不复制 |
| GUI responsiveness | PASS | preview/download/FFmpeg/cancel/exit event loop；最大20ms计时器gap0.037654秒；window move/settings打开 |
| GUI代理专项响应 | NOT TESTED | 网络代理和GUI各实测，未合成代理GUI计时专项 |
| Unit regression | PASS | stdlib unittest 9项；真实YoutubeDL与PP构造、参数保留、类型拒绝、preset、状态、安全、重复入队 |
| Frozen executable packaging | NOT TESTED | freeze_support已加，不在B0.1打包范围 |
| B2 FormatProfile/selector与产品UI | NOT IMPLEMENTED | 明确按用户要求推迟；当前原生formats/排序、bv+ba无固定上限 |

## 本地证据索引

根目录：`D:\YouTube视频下载\B01 evidence`，不提交媒体与签名URL。

- `1080p-selected.json/1080p.result.json/1080p.ffprobe.json/1080p.verify.json`
- `4k-selected.json/4k.result.json/4k.ffprobe.json/4k.verify.json`及cancel/resume记录
- `audio-selected.json/audio.result.json/audio.ffprobe.json/audio.verify.json`
- `8k-native/media-results.json`记录571/251、三阶段cancel、resume和完整MKV下载；原full-decode61bytes警告保留
- `8k-native/final-8k-result.json/final-ffprobe.json/final-decode-progress.log/final-decode-errors.log`记录最终MP4和全片decode；不以旧失败文件替代最终结果
- `network-final-2/network-results.json`，`gui-final/gui-results.json`，`failure/failure-result.json`
- workspace外层 `B01-unit.log/B01-network-final-2.log/B01-gui-final.log/B01-failure-final.log/B01-8k-finish-final.log`为运行记录

只有对应实际运行记录才PASS。未跑全片的1080P/4K/audio清楚标为10秒抽查；8K必须全片验证，已做到。报告里的源码调用链/类型检查与实网执行证据分别叙述，不混为全部平台和认证形式验收。
