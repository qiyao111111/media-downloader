Media Downloader @VERSION@ — Release Candidate / 候选版本
Source-quality media downloader / 优先保存视频源实际提供的最高原始画质

中文
解压 Portable ZIP，然后双击 MediaDownloader.exe。无需安装 Python、FFmpeg
或 QuickJS。Portable 目录必须可写；安装版从开始菜单启动，正常使用无需管理员权限。
首次启动选择语言和默认下载目录。粘贴链接 → 解析 → 选择画质、封装格式和
保存目录 → 开始下载。画质来自当前视频源；默认保留原始画质并匹配音频。
仅音频在下载页面选择。取消保留部分下载文件；重试可继续下载。

设置 → Cookies：cookies.txt 用于需要登录状态的视频。请勿分享 cookies.txt。
Firefox 尽力支持，Windows Chrome/Edge 直接读取为实验性功能。
设置 → 代理：支持 HTTP、SOCKS5、SOCKS5H，留空不使用代理。
设置 → 运行环境：查看实际版本，运行诊断。日志页面可复制、清空视图、打开日志目录。
设置 → 关于或帮助菜单：查看使用说明和第三方许可。
部分 AV1/VP9/Opus 文件需要支持这些编码的播放器，不会自动降画质或安装 codec pack。
YouTube 上游可能返回 403 或登录验证；程序不保证每次请求都成功。
仅下载你有权保存或使用的内容。

Portable 配置/历史/日志在 EXE 同目录的 config/data/logs；安装版位于
%LOCALAPPDATA%\MediaDownloader。保存设置后重启会保留设置和历史。
正常卸载保留用户下载文件及配置；删除 Portable 目录会删除其中的配置和缓存。
请将视频保存到 Portable 目录以外，并在删除前关闭应用。

English
Extract the Portable ZIP and double-click MediaDownloader.exe. No Python,
FFmpeg or QuickJS installation is required. Keep the Portable folder writable.
Installed users launch from the Start Menu; normal use does not need elevation.
First launch: choose language and default download folder.
Paste a link → Analyze → choose Quality, Container and Save to → Download.
Quality options come from the current source. Best Quality preserves source
video quality and pairs audio; Audio Only is available on the Download page.
Cancel keeps partial downloads. Retry can resume them.

Settings → Cookies: use your own cookies.txt for authenticated videos.
Do not share your cookies file. Firefox is best effort; Chrome/Edge browser
extraction on Windows is experimental.
Settings → Proxy: HTTP, SOCKS5 and SOCKS5H; leave blank for no proxy.
Settings → Runtime: actual versions and diagnostics. Logs: copy, clear the
view, or open the log folder. Clearing the view does not delete log files.
About / Help: instructions and Third-party licenses.
AV1/VP9/Opus may require a compatible player. No automatic quality reduction
or codec-pack installation. YouTube may refuse requests or require authentication.
Only download content you have the right to save or use.

Portable config/history/logs live in config/data/logs beside the EXE.
Installed data lives in %LOCALAPPDATA%\MediaDownloader. Settings Save is explicit.
Uninstall preserves downloads and user configuration. Deleting Portable removes
its local data; keep downloaded videos outside it and close the app first.

Third-party materials: THIRD_PARTY_NOTICES.txt, licenses/, SOURCES/, source-offer/.
No telemetry or automatic log upload. Updates are user-triggered and read-only;
update the application bundle to update its bundled components.
Internal RC: Clean Machine Gate = NOT TESTED.
Public Distribution Gate = NEEDS LEGAL REVIEW. This is not a v1.0 public release.
