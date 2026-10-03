# B1 Removed Features

删除前`rg`定位全部声明/读取/应用/PP引用；删除后再次搜索并跑16项测试与真实GUI/runtime烟测。无删除下载核心、yt-dlp extractor或FFmpeg引擎。

| Feature | Files | Reason | Dependency Check | Regression Result |
|---|---|---|---|---|
| UI重复yt-dlp options映射（约130行） | gui/widgets/settings_panel.py | 输入应与参数生成解耦 | collect_opts唯一业务调用在MainWindow；其调用统一manager.build_options；tests GUI mock保留；核心builder接管目录/subtitle/default转换 | PASS：原10 tests、GUI1080P/4K/audio/proxy/file、8K |
| SponsorBlock控件入口 | gui/widgets/settings_panel.py | 非首版能力 | sponsorblock_combo/cats_edit只在此文件create/collect/apply；core仅读字符串flag，测试只构造PP，无依赖UI字段；移除后UI输出空flag | PASS：GUI启动/预设/烟测；PP构造兼容继续PASS |
| Split Chapters控件入口 | gui/widgets/settings_panel.py | 非首版分割功能 | cb_split_chapters仅此文件create/collect/apply；core靠split_chapters flag，不依赖checkbox；首版UI输出False | PASS：GUI/原核心测试 |
| 私有副本状态定义 | core/task.py、GUI状态判断 | 避免多状态协议 | TaskStatus唯一生产定义移至models；所有判断使用它，旧值仅normalize入口 | PASS：终态保护、Legacy history、Cancel/Retry/FFmpeg失败 |
| 旧history/option实现位置 | core/history.py、configs/ydl_opts.py | 明确持久化/参数职责 | 搜索所有imports后，git mv到service/core；旧import shim仅重导出 | PASS：既有10tests旧import仍工作 |
| 日志handler直接跨线程写Qt | gui/widgets/log_viewer.py | 主线程边界 | 唯一QTextEditHandler.emit改queued Signal；roothandlerclose移除 | PASS：GUI最大gap与exit child0；日志测试 |

移除UI入口不代表移除其底层兼容API：SponsorBlock/FFmpegSplitChapters原生builder适配暂Defer，避免破坏既有测试和高级配置调用者。没有把这些API冒充第一版正式支持。

不删除已引用依赖、styles、preset、字幕/metadata或其它高级设置；其调用关系尚与现有UI/持久化交织，inventory明确Defer。保留两个兼容import，不复制实现。实际依赖删除=0，平台功能新增=0。
