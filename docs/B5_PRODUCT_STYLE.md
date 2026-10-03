# B5 Product Style

Product: **Media Downloader**. Version is read only from `app/version.py`: **0.9.0-rc1**.
Positioning: Source-quality media downloader / 优先保存视频源实际提供的最高原始画质.
Original project attribution is retained in the MIT license, notices and executable copyright metadata.
No official YouTube relationship or guaranteed access is claimed.

| Surface | English | 简体中文 |
|---|---|---|
| Navigation | Download / Queue / History / Settings / Logs | 下载 / 队列 / 历史记录 / 设置 / 日志 |
| Actions | Analyze / Download / Save / Browse | 解析 / 开始下载 / 保存 / 选择文件夹 |
| Quality | Best Quality (Recommended) | 最高画质（推荐） |
| Container | Auto (Recommended) | 自动（推荐） |
| Audio | Audio Only | 仅音频 |
| Status | Queued / Analyzing / Ready / Downloading / Post-processing / Completed / Failed / Cancelled | 排队中 / 解析中 / 准备完成 / 下载中 / 处理中 / 已完成 / 失败 / 已取消 |
| Settings groups | General / Downloads / Cookies / Proxy / Runtime / Advanced / About | 常规 / 下载 / Cookies / 代理 / 运行环境 / 高级 / 关于 |

The download page presents URL, Analyze, thumbnail/title/uploader/duration/highest quality, Quality, Container,
save folder, Download. Raw format IDs and codec strings are read-only advanced details.
Labels consume the existing Core profiles. H264/OPUS display spelling becomes H.264/Opus without changing values.
AV1/VP9/Opus compatibility hints never change the chosen format, FPS, HDR or video encoding.
Audio Only disables quality/container controls. Missing UI measurements display `--`.

Queue retains the internal state strings; translations are presentation only. Merging uses an indeterminate bar
and “Merging audio and video…” rather than suggesting the final file is ready at 100%.
History supports opening files/folders, copying URLs, downloading again and removing records through existing handlers.
Empty states, keyboard focus, native paste, single-URL Enter Analyze and Esc dialog close are retained.
Clear History requires confirmation; clearing the visible log does not delete the log file.

Page margins/spacing: 16 logical pixels; settings section spacing: 10; controls: 24 pixel minimum content height
plus padding; primary Download is pinned outside its scrolling form. Minimum main window: 720×440 logical pixels.
Font: Segoe UI with Windows fallback; no bundled font. System/Light/Dark reuse two Qt style sheets and OS color scheme.
Primary Analyze/Download/Save use accent colors, secondary actions use neutral outlines, Cancel uses the destructive color.
The existing simple download-arrow icon is reused at 16/32/48/256 sizes; no new brand assets or dependencies.
Long metadata titles wrap, are limited to 240 displayed characters and retain a full tooltip.
High-DPI verification uses Qt process scaling, not an assertion of changing the host's Windows display settings.

No restore-defaults feature, account workflow, RTL or Traditional Chinese is introduced.
Existing atomic Settings/history persistence, worker shutdown and downloaded-file ownership remain unchanged.
