# B0 安全与外联审计

基线 `0e42112dae627c10ce159ece0ef97594ccd27d39`；静态扫描覆盖全部受控源码，另追踪本机 yt-dlp 2026.8.19 的代理与 FFmpeg 关键路径。不是全依赖漏洞扫描，也没有网络抓包；未观察到不代表不存在。

## 搜索结果与信任边界

检索 cookie/cookies/cookiesfrombrowser/browser/authentication/login/token/proxy/socks/http/https、requests/httpx/urllib/aiohttp/socket/api/telemetry/analytics/update/github/webhook/upload，以及 eval/exec/pickle/shell=True/os.system/subprocess/tempfile。项目无 eval、Python exec、pickle、shell=True、os.system、直接 subprocess、HTTP client、上传、自动下载 EXE、自动更新实现。`QApplication.exec/QDialog.exec/QMenu.exec` 是 Qt 事件循环，不是代码执行。

URL 经按行去重后进入 YoutubeDL.download；filename template、输出路径、代理、Cookie 路径均直接作为字典参数透传；没有拼接 shell 命令。yt-dlp FFmpegPostProcessor 使用参数数组 Popen，未在审计路径发现 shell 注入。自定义参数界面是明确字段和格式字符串，无通用命令行执行框。

输出模板允许绝对路径/`../`，可写到下载目录外。这是本地高级用户授权配置能力；没有证明远程标题能突破 yt-dlp sanitization。项目未提供目录约束/覆盖确认，仍需防止用户误配置。自定义 ffmpeg/external_downloader 依赖可信本机可执行文件；PATH 被劫持属于执行信任边界。用户 URL 可访问其它 yt-dlp 支持站点或内部地址，没有协议/域名白名单；本地桌面输入不自动等于服务端 SSRF。未证明任意远程代码执行或 P0 风险。

## Cookies 与凭据

`settings_panel.py:310/646` 提供 cookiefile 和 chrome/edge/firefox/safari/brave；`ydl_opts.py:129` 转成 `(browser,)`，cookiefile 原键透传。浏览器 profile/keyring 不可配置。Windows 浏览器锁与加密兼容性委托 yt-dlp；未读取用户真实 Cookie，未做登录成功测试。

AppSettings 和 PresetManager 使用明文 JSON。保存 username/password、包含代理 user:pass 的 URL、cookiefile 路径、浏览器选择；不会把 Cookie 文件内容复制到 AppSettings，但外部 cookies.txt 本身是敏感明文，yt-dlp 可能保存/更新 jar。测试只用 `AUDIT_DUMMY`，确认密码可从 JSON 直接读出。Password UI 遮罩；Proxy/Geo Proxy QLineEdit 不遮罩。用户预设收 collect_opts，也可能把凭据明文写入 user_presets.json。

没有独立 token 字段，无开发者服务器上传代码；Cookie 由 yt-dlp 向匹配站点发送是认证所需外联。不能承诺所有依赖绝不记录敏感数据：GUI `_on_error:236` 直接显示异常文本，无脱敏；历史也保存原始 URL（可能包含 token），日志不清洗。未观察到完整 Cookie/Authorization/代理密码实际进入本次日志，仍标记潜在泄露风险 P2；明文凭据保存为 P1。

## Proxy

collect_opts:667 → build_opts → 每任务 YoutubeDL.params.proxy；同批任务使用相同代理快照，后续修改不会更新已有任务。无硬编码代理。HTTP、SOCKS5、SOCKS5H 可透传，安装环境 UrllibRH 支持这些 scheme；未对真实代理服务做端到端连接测试。username/password URI 支持由依赖解析；UI 明文显示且设置文件明文持久化。

**HTTPS 目标通过 HTTP CONNECT 代理，与 `https://` 代理服务器不同。** 官方 uv sync 只有 urllib handler；实测 `https://127.0.0.1:9` 报需 requests/curl_cffi。README/工具提示声称 HTTP/HTTPS/SOCKS 的范围大于默认依赖能力。不为审计增加依赖或修改产品。

## 所有可确定的域名/网络类别

| 域名/类别 | 触发 | 必需性 | 证据 |
|---|---|---|---|
| youtube.com / www.youtube.com / youtubei.googleapis.com 等 YouTube API | 用户解析/下载 YouTube | 下载必需；域名由 extractor 变化 | yt-dlp YouTube extractor；本次返回 YouTube metadata |
| *.googlevideo.com | 视频/音频 CDN 请求 | 下载必需 | 本次 metadata formats 的 stream URLs |
| i.ytimg.com（可能其它 ytimg 子域） | thumbnail URL、下载封面 | 封面功能可选；GUI 不请求图像 | 本次 metadata thumbnail URL |
| sponsor.ajay.app | 可选 SponsorBlock PP | 非核心必需，用户启用时才需要；当前 action 参数错误阻断 | configs/ydl_opts.py:107；依赖 postprocessor/sponsorblock.py:34 |
| github.com / api.github.com / raw.githubusercontent.com | 克隆、维护信息核查、手动升级 | 开发/维护可选；应用启动未调用更新 API | README；无 app update 调用 |
| pypi.org / files.pythonhosted.org | uv/pip 装依赖 | 开发安装必需；非应用自动外联 | uv sync |
| 任意 yt-dlp extractor/外部下载器所需域名、用户代理端点 | 用户提交其它网站 URL/选择工具 | 依用户行为 | 无 URL 域限制，传给 yt-dlp |
| JS remote components 所用 GitHub/npm 分发端点 | 显式配置 remote_components 才可能获取 | 默认未启用；GUI 无此选项 | YoutubeDL 默认 set() |

程序启动源码本身没有网络请求、遥测、analytics、webhook、开发者 API、上传 Cookie 或后台更新。不能有限枚举任意站点 extractor 将来的全部域名；上表给出本次 YouTube 路径和源码可达可选路径，**不是抓包确认的全流量列表**。yt-dlp 的插件自动加载及外部工具是额外供应链边界。

## 日志/供应链结论

依赖只下限无上限，uv.lock 被 gitignore，官方 uv sync 随时间取不同版本；未锁定已验证组合。FFmpeg 使用本机 PATH，不校验签名/hash，不随项目提供，不能据此保证二进制来源。应用无自动更新减少后台下载面，但 YouTube 提取器仍需明确手动升级策略。安全建议仅列入 B0_RISK，本阶段不修复。
