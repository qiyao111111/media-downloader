# B0 功能矩阵

基线 `0e42112dae627c10ce159ece0ef97594ccd27d39`，Windows 11 x64 / Python 3.13.13 / yt-dlp 2026.8.19。
PASS 只表示 Notes 所述范围实际验证成功；PARTIAL 表示已有部分能力/源码路径但缺少完整验证或存在限制；NOT TESTED 不以依赖宣称替代测试。没有任何条目代表所有网站/机器都通过。

| Feature | Status | Evidence | Notes |
|---|---|---|---|
| 1080P | PASS | presets.py 1080p；T1 | 399+251，全片；ffprobe 1920×1080 AV1+Opus |
| 1440P | PARTIAL | metadata formats 308/400/623；可手输 height | 无专用预设，未下载1440P |
| 4K | PASS | T2，401+251 | 全片；ffprobe 3840×2160 AV1+Opus；MKV |
| 8K | NOT TESTED | format输入不设上限 | 未用4320P源验证，无专用预设 |
| AV1 | PASS | T1/T2 | 实际下载、合并、前5秒软件解码 |
| VP9 | PARTIAL | metadata 315(vp9)/628(vp09) 等 | 格式读取确认，未下载VP9 |
| H264 | PARTIAL | metadata 299(avc1.64002a) 等 | 格式读取确认，未下载H264 |
| HDR | NOT TESTED | 可自定义format/sort | 无专用开关，源未验证HDR |
| Highest Video | PARTIAL | ffmpeg_utils.py bv*+ba/b；T2 | 本次2160P；无ffmpeg降级b，sort/容器偏好不保证绝对最高 |
| Highest Audio | PARTIAL | ba；本次251 Opus | 本次最佳选择已下载；不是所有源的最高码率承诺 |
| Audio/Video Merge | PASS | T1/T2；yt-dlp Merger | 两条独立流、最终双stream、解码成功 |
| MP4 | PASS | T1 | AV1+Opus；原生Windows播放器兼容性未测 |
| MKV | PASS | T2 | AV1+Opus；ffprobe与解码成功 |
| WebM | PARTIAL | T5 | 同一YouTube产物拆成5秒独立流后经yt-dlp FFmpegMergerPP合并并完整解码；未做GUI完整WebM下载 |
| Cookies.txt | PARTIAL | settings_panel.py:329/650；ydl_opts.py:134 | 正确cookiefile透传；未用真实认证Cookie测试 |
| Chrome Cookies | PARTIAL | browser combo；tuple转换 | 不访问个人浏览器；Windows解密/锁兼容未测；GUI preview丢设置 |
| Edge Cookies | PARTIAL | 同上 | 同上 |
| Firefox Cookies | PARTIAL | 同上 | 同上 |
| HTTP Proxy | PARTIAL | collect_opts:667 → proxy；Urllib handler | 参数路径确认；无真实代理端到端测试；preview忽略 |
| HTTPS Proxy | FAIL | T9 | https://代理默认缺 requests/curl_cffi；HTTPS目标通过HTTP代理另论 |
| SOCKS5 Proxy | PARTIAL | Urllib支持socks5；proxy透传 | 未连真实SOCKS5；preview忽略 |
| SOCKS5H Proxy | PARTIAL | installed networking/_helper.py | scheme解析存在；未做真实远程DNS/代理认证测试 |
| Proxy username/password | PARTIAL | URI透传；UI/JSON | 后端支持解析；无实连；明文显示与保存 |
| Playlist | PARTIAL | noplaylist/playlist_items；YoutubeDL.download | 委托yt-dlp，单任务行；无完整playlist运行验证 |
| Queue | PARTIAL | manager.py ThreadPoolExecutor；T10 | 5个mock任务在max_workers=2下峰值2，排队执行；未做压力/持久化恢复；取消不移出Future队列 |
| Concurrent Downloads | PARTIAL | manager.py:19；T7 | 默认3，启动读取设置；UI改7仍3；fragment不是任务并发 |
| Concurrent Fragments | PARTIAL | settings_panel.py:445/677 | 独立传参；未对分片并发做实测 |
| Resume | PASS | T4 | 强制结束项目核心下载进程，重启从65622351字节继续；格式/路径一致 |
| Cancel | PARTIAL | T6 | 下载hook中取消成功，.part保留4193280字节；解析/合并取消未验证且无立即中断 |
| Cancel All | PARTIAL | MainWindow._on_cancel_all → manager.cancel_all | Event实现；未多任务实测 |
| Pause All | NOT IMPLEMENTED | 无pause API/按钮 | 不把取消视作暂停 |
| Download History | PARTIAL | history.py JSON；MainWindow restore；T10 | 临时JSON重载实测通过；无文件路径、失败原因、实际格式/参数；progress固定0 |
| Logging | PARTIAL | log_viewer.py；main_window.py:236 | 无文件/滚动/脱敏；yt-dlp stdout非完整GUI日志 |
| Auto Update | NOT IMPLEMENTED | 全源码搜索 | 无更新检查/EXE下载/自动替换 |
| Windows EXE | NOT IMPLEMENTED | pyproject.toml；release assets=[] | 无打包spec/工作流；用户免Python尚未实现 |
| Chinese Path | PASS | T1–T6 | 源码与下载目录含中文，输出目录额外含空格，FFmpeg真实处理成功 |
| Unicode Filename | PARTIAL | prepare_filename 中文+禁止字符验证 | 标题sanitization正常；最终完整Unicode basename/emoji/长名未实测 |
| Windows 10 | NOT TESTED | 本机只有Win11 | 不推断兼容性 |
| Windows 11 | PASS | T0、T1/T2/T3 | 本机26200、x64；非全部Win11版本认证 |
| Chinese Username | NOT TESTED | 本机用户名thang | 不等同于中文目录 |
| Long Filename | NOT TESTED | 无应用trim_file_name/长路径验收 | 需单独长标题/深目录测试 |
| Metadata title/formats | PASS | 项目extract_info：53 formats | 真YouTube URL；格式对话框源码可显示 |
| Thumbnail display | NOT IMPLEMENTED | FormatPreviewDialog没有图像组件 | metadata有thumbnail URL，封面获取URL已确认，图片下载/显示未实现 |
| Audio only | PARTIAL | T3 MP3可解码 | 提取成功，但原预设实际先下载401+251的4K视频，非纯音频流下载 |
| Rate Limit | FAIL | T7 | 50K直接透传str，slow_down TypeError |
| Match Filter | FAIL | T7 | list不可调用 |
| Date Range | FAIL | ydl_opts.py dateafter/datebefore | embedding API读取daterange，不执行这些CLI字段 |
| SponsorBlock | FAIL | T7 | PP不接受action参数 |
| Metadata/Chapters embedding | FAIL | T7 | 两开关开启仍无FFmpegMetadataPP |
