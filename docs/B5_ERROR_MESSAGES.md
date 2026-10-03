# B5 Error Messages

Friendly messages are UI-only. Core error types, retry policy and failure states remain unchanged.
Expanded details and local logs use existing credential redaction; Cookie/token/password values must not appear.
The normal desktop exception hook presents a friendly dialog and writes the redacted traceback to the local log.
No crash reporting, telemetry or automatic log upload is added.

| Key | English | 简体中文 |
|---|---|---|
| error.invalid_url | Enter a valid video or playlist URL. | 请输入有效的视频或播放列表链接。 |
| error.unavailable | This video is unavailable or access is restricted. | 此视频不可用或访问受到限制。 |
| error.auth | Authentication is required. Configure your own cookies.txt file. | 需要登录状态，请配置自己的 cookies.txt 文件。 |
| error.cookies | Unable to read browser cookies. This feature is experimental on Windows. Use a cookies.txt file instead. | 无法读取浏览器 Cookies。Windows 上该功能为实验性支持，请改用 cookies.txt。 |
| error.cookie_file | Unable to read the cookies.txt file. Check its path and Netscape format. | 无法读取 cookies.txt，请检查路径和 Netscape 格式。 |
| error.proxy | Unable to connect through the proxy. Check its address and credentials. | 无法通过代理连接，请检查地址和凭据。 |
| error.format | No valid format was found. Analyze the video again. | 没有找到有效格式，请重新解析视频。 |
| error.ffmpeg_missing | FFmpeg is missing. Check Runtime Health. | 缺少 FFmpeg，请检查运行环境状态。 |
| error.merge | Media merging failed. Open the logs for technical details. | 媒体合并失败，请打开日志查看详细信息。 |
| error.disk | Not enough free disk space. | 可用磁盘空间不足。 |
| error.network | The network request failed. Check your connection and retry. | 网络请求失败，请检查连接后重试。 |
| error.challenge | YouTube rejected this request. Try again later, or configure a cookies.txt file if authentication is required. | YouTube 暂时拒绝了本次请求。可以稍后重试，或在需要时配置 cookies.txt。 |
| error.403 | The server rejected this media request. Retry, or configure cookies.txt if the video requires authentication. | 服务器拒绝了本次媒体请求。请重试；如果视频需要登录状态，可配置 cookies.txt。 |
| error.cancelled | The task was cancelled. Retry to resume the download. | 任务已取消，可重试以继续下载。 |
| path_missing | Choose an existing download folder. | 请选择已存在的下载目录。 |
| error.generic | The operation failed. Open the logs for technical details and retry. | 操作失败，请打开日志查看技术详情后重试。 |

Cookies.txt is the supported path. Browser read failures recommend cookies.txt; Chrome/Edge are experimental and Firefox is best effort.
The proxy field is masked and accepts the existing HTTP/SOCKS5/SOCKS5H URLs; a blank value means no proxy.
HTTP 403/challenge text does not assign an unproven cause to the IP, account or Cookie.
Disk-space estimates are not invented: the existing Core exposes no reliable required/available estimate in its disk error.
Audio/video merge errors retain the technical cause in details. Cancelled tasks retain the cancelled internal state.
Folder validation checks an existing directory and offers Browse; it does not introduce a new path creation policy.
Runtime Ready/Warning/Missing labels show actual versions; technical paths are available in diagnostics.
Codec compatibility warnings do not install a player/codec pack or perform video conversion.
