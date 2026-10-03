# B1 Feature Inventory

2026-10-02，扫描全部生产模块、widgets、preset、API builder、入口、依赖及live tests。Keep/Remove/Defer针对第一版入口；依赖证明先于删除。

| Feature | Source Location | Current Status | Keep / Remove / Defer | Reason | Risk |
|---|---|---|---|---|---|
| YouTube单视频/批量URL | url_input.py、MainWindow、DownloadManager | 实测GUI下载 | Keep | 首版核心 | 无新平台；通用yt-dlp backend保留 |
| Playlist/选集 | settings_panel.py、option_builder.py、YoutubeDL | 参数保留、原生执行 | Keep | 首版核心 | 本阶段未完整大型playlist专项 |
| 默认source最高画质 | ffmpeg_utils.get_default_format / option_builder | bv+ba；真实8K回归 | Keep | 已验证路径、无分辨率上限 | native sort不等于B2最终策略 |
| 自定义分辨率/format入口 | settings_panel、FormatPreviewDialog | 实际formats/用户选择 | Keep | 首版入口 | 友好标签/排名延后 |
| FormatProfile / HDR codec排名 | models/format.py | 字段接口 | Defer | B2正式实现 | 不声称HDR/60FPS整套验收 |
| Audio MP3/FLAC | presets、FFmpegExtractAudio | MP3实测，FLAC未专项 | Keep | 首版Audio Only | 只扩展数据边界不转码中心 |
| cookies.txt | cookies_manager/credentials/runtime | 受控认证PASS | Keep | SUPPORTED路径 | 真实账号文件仍不读取/输出内容 |
| Firefox/Chrome/Edge Cookies | cookies_manager / native yt-dlp | API保留 | Keep | Best Effort/Experimental便利 | 外部锁/解密/登录限制 |
| 用户密码/netrc | 现有认证控件/builder | 原有适配 | Defer | 不是账号系统，避免误删原生接口 | UI后续可精简；session-only密码 |
| HTTP/SOCKS5/SOCKS5H | proxy_manager | 两阶段真实转发PASS | Keep | 首版网络核心 | HTTPS代理server额外backend未验收 |
| geo_verification_proxy | settings_panel / builder | 原有API | Defer | 高级功能，保留兼容 | 无专项实网 |
| Queue/concurrency/去重 | DownloadManager | model/state/event测试 | Keep | 首版核心 | downloads与fragments分开 |
| Progress/speed/ETA | DownloadRecord / task_table | 实际hooks | Keep | 首版核心 | playlist显示job级最近条目 |
| Cancel/Resume/Retry | runtime/task/manager/UI | GUI与8K实测 | Keep | 核心稳定能力 | 只终止拥有的进程 |
| History | HistoryService | JSON规范接口及旧值兼容 | Keep | 复用存储无DB迁移 | 非atomic写仍待收尾 |
| Settings/Preset | SettingsService/Settings/DownloadPreset | 保护长期设置 | Keep | 稳定基础 | 部分模型字段仅预留 |
| Logs | logging_service/LogViewer | rotation/Qt queued delivery | Keep | 安全与诊断 | 不上传/telemetry |
| FFmpeg/ffprobe | ffmpeg_utils / yt-dlp PP | discovery/version/probe；原生merge | Keep | 必需工具 | 不造第二merge engine |
| 字幕/缩略图/描述/infoJSON/comments | settings_panel / builder / With Subtitles | 原有控件与PP | Defer | 涉及已有preset/配置；非B1重写范围 | 不承诺首版完整专项验收 |
| metadata/chapters embed | builder | 既有真实PP | Keep | 无损输出属性 | 与章节拆分不同 |
| SponsorBlock UI | settings_panel.py | 已移除 | Remove | 不属第一版，core无引用控件 | 底层API适配Defer、构造测试保留 |
| Split Chapters UI | settings_panel.py | 已移除 | Remove | 独立分割非核心 | 底层PP兼容Defer |
| video recode/remux | settings_panel / builder | 原有显式选项 | Defer（recode）/Keep（remux） | remux无损容器处理需要；不扩建转码中心 | 最高画质不自动recode |
| external downloader | settings_panel / builder | 既有选项 | Defer | 首版原生下载即可；不装依赖 | 为配置兼容保留 |
| archive/filter/date/size/sleep | settings_panel / builder | 当前API类型已修 | Defer | 现有设置影响下载，不能无证据删除 | 非核心专项未测 |
| theme/language/about | theme_manager/menus/settings | 原有实现 | Keep（基础设置） | 不品牌化、不美化 | 原3.0/3.1标识差异P3 |
| 其它平台/云/账号付费/AI/updater | 无独立实现 | NOT IMPLEMENTED | Defer | 明确禁止新增 | yt-dlp通用extractor是依赖，不新增平台产品支持 |

依赖：PySide6/PyYAML/yt-dlp均Keep；不存在requirements.txt。目标目录建议不作为机械移动标准。删除证据和回归见B1_REMOVED_FEATURES。
