# B4 Runtime Architecture

```text
App / Settings / Preview / DownloadManager
  -> RuntimePaths + Runtime Manager
     -> bundled yt-dlp Python package + matching EJS
     -> bin/ffmpeg.exe + its shared DLLs
     -> bin/ffprobe.exe + its shared DLLs
     -> bin/runtime/deno.exe
```

保持 B1/B2/B3 的 Manager、spawn worker、状态记录与原生 yt-dlp 下载/后处理链路。
`core/format_selector.py` 未修改；没有更改 Best Quality 排序、分辨率上限或 UI 页面结构。

## Paths

`app/paths.py` 的不可变 RuntimePaths 在启动时统一解析，不依赖 cwd。

| Field | Source | Portable frozen | Installed frozen |
|---|---|---|---|
| application_dir | repo root | EXE parent | EXE parent |
| resources_dir | repo root | sys._MEIPASS / _internal | sys._MEIPASS / _internal |
| runtime_dir | repo/bin | application_dir/bin | application_dir/bin |
| config_dir | repo/configs，保留旧兼容 | application_dir/config | LOCALAPPDATA/MediaDownloader/config |
| data_dir | repo/data；旧 history 仍在 configs | application_dir/data | LOCALAPPDATA/MediaDownloader/data |
| logs_dir | repo/logs | application_dir/logs | LOCALAPPDATA/MediaDownloader/logs |
| temp_dir | repo/temp | application_dir/temp | LOCALAPPDATA/MediaDownloader/temp |
| download_dir | repo/video | 用户 Downloads/MediaDownloader | 用户 Downloads/MediaDownloader |

Settings 可以更改下载目录。存在 `portable.flag` 才判定 Portable；没有 marker 的 frozen
payload 是 Installed。两个模式的配置/数据目录独立。Portable 必须位于可写目录，
不应把配置写入 Program Files。安装版用户数据位于 LOCALAPPDATA。

## Tool resolution / options

`core/runtime_manager.py` 是唯一新运行时发现和健康检查入口。
优先 bundled；source 允许 FFmpeg/FFprobe PATH fallback；frozen 不 fallback 到开发机 PATH。
原有用户显式 FFmpeg location 仍允许，但需要存在的本地工具，不接受网络 executable URL。

统一 options builder 注入绝对 `ffmpeg_location`、`js_runtimes={'deno':{'path':...}}`、
应用 temp 下 cachedir 和空 remote_components；Preview/Download 经过同一 builder。
worker 环境设置 DENO_DIR 到应用 temp、DENO_NO_UPDATE_CHECK=1，避免另一套宿主运行时/cache。
程序不修改用户/系统 PATH，不下载 npm/EJS，不自行执行浏览器解密。

正常 source-quality 组合在任务创建前检查 FFmpeg 和已知 estimated size；
known size > 当前下载目录 free space 阻止，unknown size 不阻止。
高级自定义 expression / playlist 沿用原生 worker 的 ReadyPP/合并检查，在开始媒体下载前保留
可诊断 FFmpegError。没有重写下载引擎。

## Runtime Health

统一使用 READY / ERROR / NOT_INSTALLED；WARNING 为保留状态，本次无需要警告的实测条目。
检查 app version、OS、architecture、yt-dlp metadata、ffmpeg/ffprobe -version、deno --version
及 config/download/temp 可写性。版本从工具输出解析，UI 没有写死 FFmpeg 8.0。
详细检测通过 Manager executor 回传 Qt queued signal，不阻塞 UI；启动无网络、更新或视频测试。
启动仍会异步探测本地版本，每个 executable 有 10 秒超时。

Settings 的 Run Diagnostics 显示摘要和路径 tooltip；Check yt-dlp Update 仅用户主动触发，
异步只读查询 GitHub。CLI `--diagnostics <absolute.json>` 使用同一 health，检查默认下载位置；
GUI 检查当前选择的下载目录。

缺 JS 显示 NOT_INSTALLED 和可能影响格式可用性的提示，应用可继续启动/解析。
缺 FFmpeg 时，需要合并/音频处理的路径提供可诊断错误；Preview 可以继续。
诊断不枚举 Cookie 数据，不输出代理密码/Authorization/token。日志继续走 SafeFormatter。
frozen 无 stderr 的未处理启动异常写安全 startup-error.log（覆写单文件）。

temp 包含可再生 Deno/yt-dlp cache；应用关闭后可清理，不需要恢复其中的数据。
atomic 写入的临时文件正常/异常 finally 清理；强制终止遗留文件读入时忽略。
yt-dlp .part/.ytdl 位于下载目录，取消保留供 Resume，成功后原生 merge 清理中间流。

Portable/Installed health 和子进程清理证据见 `B4_RELEASE_VALIDATION.md`。
