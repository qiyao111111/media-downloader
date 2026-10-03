# B1 Settings Model

长期存储仍是`configs/app_settings.py:AppSettings` JSON；应用入口使用`services.settings_service.SettingsService`复用它。typed model在`models.settings.Settings`，不为接口准备迁移数据库或机械改全部key。

| Model Field | Existing Store / Usage | Status |
|---|---|---|
| download_directory | download_path→core builder paths.home | 当前使用 |
| filename_template | outtmpl | 当前使用 |
| default_quality_mode | format空→source/bv+ba；非空保留用户表达式 | 当前使用 |
| default_container | merge_output_format | 当前使用 |
| audio_only_format | audio_format | 当前使用 |
| cookies_source/cookies_path/browser | cookiefile/cookiesfrombrowser | 当前使用；只许一个source |
| browser_profile | 原生tuple API可显式profile | model预留，GUI无控件 |
| proxy_enabled/proxy_url | proxy空→direct | 当前使用，敏感userinfo只在会话 |
| ffmpeg_path | ffmpeg_location | 当前使用/native PP |
| ffprobe_path | tools helper能发现FFprobe | model预留，无新UI持久化映射 |
| max_concurrent_downloads | max_workers | manager pool配置，1..10 |
| concurrent_fragments | concurrent_fragment_downloads | native分片数，独立pool |
| retries/fragment_retries | native defaults/已有API传入 | model预留默认10，无新增UI |
| theme/language | existing keys | 保留基础设置，不美化 |

DownloadPreset独立于Settings，`download_options()`排除PROTECTED_SETTINGS：proxy/geo_proxy、cookie source/path/browser/profile、下载目录、outtmpl、FFmpeg/FFprobe路径、账户会话、worker数/theme/language。`merge_preset`先保留现有settings再仅合并preset负责的下载字段；embedsubtitles映射也集中在service。

PresetManager.save_user_preset只保存DownloadPreset允许的options；GUI.apply_preset走同一merge。旧preset如果包含保护字段，应用时也不能覆盖长期设置。B0.1音频presetba及audio→video明确extract_audio=False继续保留。

SettingsPanel.collect_opts只返回用户输入字典；core.option_builder转换为实际API dict并删除应用key。兼容`configs.ydl_opts.build_opts`仅导出同一实现。目录/template/network/auth不会依赖Preview与Download各写一套。

密码、proxy userinfo、敏感header/token不落盘；Cookie路径与profile名称允许保存，内容不复制到JSON。保留已有legacy配置清理与加载类型保护。JSON写仍非atomic，本阶段未增加复杂store；需在产品交付前补轻量atomic保存。typed projection不是第二配置源，预留字段明确不声称已实现UI。
