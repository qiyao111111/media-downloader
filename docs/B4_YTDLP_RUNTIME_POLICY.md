# B4 yt-dlp Runtime Policy

正式策略：随 PyInstaller bundle 分发 **yt-dlp Python package**，不另带 yt-dlp.exe。
既有 DownloadManager -> spawn worker -> YoutubeDL / extract_info / 原生 FFmpeg postprocessor
已在 B0.1/B1/B2/B3 真实验证。保留同一条执行链，避免 executable/Python 两套 options
或结果协议。终端用户不需要 Python、pip 或系统 yt-dlp。

B4 lock 是 yt-dlp **2026.8.19** 与其 metadata 要求的 **yt-dlp-ejs 0.8.0**。
spec 收集两者的模块、solver 数据及 distribution metadata；health 动态获取版本。
Release 候选依赖以 requirements-lock.txt 为准，不使用宿主全局安装。
源码 pyproject 的宽版本依赖仅为已有开发入口兼容；打包必须按 lock 安装并成对验证 EJS。

Check Update：用户点击 Settings 按钮后，查询官方 latest release，显示 installed/latest。
实测 installed=2026.8.19，latest=2026.08.19（格式不同，表示同一 release）。
不在启动时联网，不下载/替换运行时，不支持 bundle 内 Python package 的单独热更新。
更新应用 release 才更新 yt-dlp/EJS，避免版本错配；因此不引入半成功替换/删除旧版本流程。

Bundled Deno 走 yt-dlp 官方 JS runtime options；不实现自有 challenge 解码器。
Preview 与 Download 的 Cookie、profile、proxy、headers 仍共用原有认证上下文。
cookies.txt SUPPORTED；Firefox BEST EFFORT；Windows Chrome/Edge EXPERIMENTAL。
Chrome/Edge 锁、DPAPI/App-Bound Encryption 限制不会被规避。

有/无 JS 同源 comparison、Windows-only PATH frozen 实测、工具绝对路径与版本
见 B4_JS_RUNTIME / B4_RELEASE_VALIDATION。来源可用性仍受 YouTube 挑战和登录要求影响。

参考：[yt-dlp 官方 EJS 指南](https://github.com/yt-dlp/yt-dlp/wiki/EJS)、
[官方 yt-dlp release](https://github.com/yt-dlp/yt-dlp/releases/tag/2026.08.19)。
