# B0.1 yt-dlp Python API 类型检查

依据：本机 `.venv` 的 yt-dlp **2026.8.19** 实际源码、`YoutubeDL` 构造和 postprocessor 构造运行测试；不是把 CLI 参数字符串当成 Python API。可复核：`python -m unittest discover -s tests -v`。来源简称：SP=`gui/widgets/settings_panel.py:collect_opts`，Y=`configs/ydl_opts.py`，D=`configs/yt-dlp.yml`，AS=`configs/app_settings.py`。

表中 Current 为修复后的实际 API 值/类型；未配置的项目是省略，并不假称 UI 已支持。

| Option | Current Value / Type | Expected Type | Source File | Runtime Impact / Fix |
|---|---|---|---|---|
| retries / fragment_retries / extractor_retries | 未设则 yt-dlp default；测试 `1` int；infinite→float inf | int / inf | Y API | 严格转换整数，拒绝负数/小数/bool |
| concurrent_fragment_downloads | 1 int；GUI >1 时传入 | positive int | SP/AS/Y | 字符串转 int，拒绝0；实际并发数不保证提升所有协议速度 |
| socket_timeout | 测试15.0 float，GUI无控件 | positive number | Y API | 字符串转 float，拒绝0/NaN/inf |
| sleep_interval / max_sleep_interval | GUI0省略；API float | nonnegative number | SP/Y | 转 float，拒绝负数/非有限值 |
| playliststart / playlistend | 未配置；API int | positive int | Y API | 转 int；GUI playlist_items 是另外的字符串选集参数 |
| skip_playlist_after_errors | 10 int | nonnegative int | D/Y | 保留并校验 |
| ratelimit | 空省略；`1M`→1048576 int | bytes/sec number | SP/Y | parse_bytes，拒绝0/负值/无效单位 |
| buffersize | 未配置；`64K`→65536 int | positive bytes number | Y API | parse_bytes，拒绝0 |
| http_chunk_size | 未配置；字符串大小→int | nonnegative bytes number | Y API | parse_bytes，0按 API 含义保留 |
| min_filesize / max_filesize | 空省略；`10M`→10485760 int | bytes number | SP/Y | 原字符串不适合大小比较；parse_bytes 修复 |
| retry_sleep_functions | `{'http': partial(_retry_delay,3.0)}` dict | dict[str, callable] | D/Y | 原 YAML int3 不可调用；改为顶层可pickle callable，真实调用 `n=3` 已测 |
| daterange | DateRange 实例 | DateRange | SP/Y | start/end 不再映射无效 CLI 式 key |
| match_filter | 可pickle partial / 原 callable | callable(info,incomplete=False) | SP/Y | 原 string 不能按 API 调用；实际 match_filter_func 校验 |
| cookiesfrombrowser | `('chrome',)` / `('edge',)` / `('firefox',)` tuple | browser/profile/keyring/container tuple | SP/Y | GUI字符串转换；已有 tuple 保留 |
| cookiefile | path str | path str / file-like | SP/Y | 路径不等于 Cookie 内容；Preview 不再丢失 |
| proxy / geo_verification_proxy | URL str，主proxy空为 `''` | str | SP/Y | 保留空proxy明确直连；认证 URL 不落盘 |
| username / password | str，本次会话 | str | SP/Y | 两阶段保留；password从持久配置剔除 |
| usenetrc | True bool（netrc勾选） | bool | SP/Y | netrc→usenetrc；不读取/打印 netrc 内容 |
| http_headers / extractor_args / impersonate | API传入，GUI无控件 | dict / dict / ImpersonateTarget | Y passthrough | 不提供假 UI；类型语义仍由实际 yt-dlp 校验，实网高级行为未验收 |
| format | 默认 `bv+ba` str | selector str / callable | SP/core/ffmpeg_utils.py | 独立视频音频，移除无FFmpeg时静默低质量 fallback；不设分辨率上限 |
| format_sort | 空省略；逗号string→list[str] | list/tuple[str] | SP/Y | 保留默认原生排序；不能声称完成 B2 排序策略 |
| paths / outtmpl | `{'home':path}` dict / template str | dict / str or dict | SP/Y | 不更改路径及模板语义 |
| merge_output_format / ffmpeg_location / download_archive | 非空 str | str / path / path or set | SP/Y | 原样传入 |
| continuedl / cachedir | True bool / False bool | bool / path or False | D/Y | 保留断点续传和禁用缓存 |
| noplaylist / skip_download / writethumbnail / writedescription / writeinfojson / getcomments | bool | bool | SP/Y | 不删 False；skip_download不能作媒体验收 |
| writesubtitles / writeautomaticsub / subtitleslangs / subtitlesformat | bool / bool / list[str] / str | bool / bool / list / str | SP/Y | write_auto_subs/sub_format重命名，语言string分割 |
| embedsubtitles | bool，另加FFmpegEmbedSubtitle | bool及PP | SP/Y | 实际构造已有PP |
| external_downloader | `{'default':name}` dict | str/dict | SP/Y | none省略；不安装外部下载器 |
| keepvideo | bool | bool | SP/Y | keep_video重命名 |
| max_downloads | int>=2，否则省略 | int | SP/Y | 原有语义保留；1被过滤的限制未在本阶段重设 |
| progress_hooks / postprocessor_hooks | parent callable list，child IPC hooks | list[callable] | core/runtime.py | 预览移除；下载保留父回调通知并去除敏感媒体URL |
| logger | SafeLogger实例 | debug/warning/error object | core/runtime.py/info_extractor.py | 保留脱敏 warning/error，debug忽略 |

## Postprocessor 参数

| GUI Option | Current Value / Type | Expected / Source | Runtime Impact / Fix |
|---|---|---|---|
| extract_audio/audio_format/audio_quality | FFmpegExtractAudio preferredcodec str/preferredquality str | SP/Y → PP dict | 音频 preset 改用ba，MP3实测；FLAC仅构造未下载验收 |
| embed_metadata/embed_chapters | FFmpegMetadata add_metadata/add_chapters bool | SP/Y → PP dict | 原CLI式addmetadata/addchapters未正确注册PP；构造测试通过 |
| remux_video/recode_video | FFmpegVideoRemuxer / FFmpegVideoConvertor `preferedformat` str | SP/Y → 当前实际PP接口 | API拼写就是preferedformat；remux copy与用户显式recode严格区分 |
| embedthumbnail/convert_thumbnails | EmbedThumbnail / FFmpegThumbnailsConvertor format str | SP/Y | 原有PP保留，非核心实网回归范围 |
| convert_subs | FFmpegSubtitlesConvertor format str | SP/Y | 原有PP保留 |
| sponsorblock_mark/remove | SponsorBlock categories list + ModifyChapters remove_sponsor_segments list | SP/Y | 删除不支持action，添加真实删除PP；构造通过，在线服务未实测 |
| split_chapters | FFmpegSplitChapters | SP/Y | 构造保留，输出多文件完整性专项未测 |

`max_workers`、语言、主题、窗口大小、preset 名称是应用设置，不是下载 API 参数；GUI collect_opts 不输出它们。AS 对加载值类型和 worker1..10 做保护。没有新增依赖或大型测试框架。
