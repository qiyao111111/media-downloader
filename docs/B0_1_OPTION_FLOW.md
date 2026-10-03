# B0.1 实际参数调用链

验证日期：2026-10-01。基线：655bcb1923d412cc7737f6bcd3b3ee220546b089。只修改核心可靠性，不进入 B1/B2。

## 配置入口与共同构造

`configs/app_settings.py: AppSettings.load/get/to_dict` → `gui/widgets/settings_panel.py: SettingsPanel.apply_settings` 恢复 GUI；`SettingsPanel.collect_opts` 读取当前控件，下载目录转换成 `paths.home`，认证、代理、字幕和格式进入同一 options 字典。

`gui/main_window.py: MainWindow._build_ydl_opts` → `SettingsPanel.collect_opts` → 无显式 format 时 `core/ffmpeg_utils.py: get_default_format` 返回 `bv+ba` → `configs/ydl_opts.py: build_opts` 合并 `configs/yt-dlp.yml` defaults → `_build_postprocessors` → `_convert_special_fields` → `_convert_api_types` → `_clean`。

这是 Preview、Download、Retry 的唯一 GUI option builder。默认 `proxy=''` 明确直连，不继承系统代理；`continuedl=True`。没有固定 2160/4320 上限。用户显式的格式约束仍按用户选择执行。

## Preview

`MainWindow._on_list_formats` → `_build_ydl_opts` → `core/manager.py: DownloadManager.extract_info(..., ydl_opts=opts)` → 现有 ThreadPoolExecutor → `core/runtime.py: run_ydl(preview=True)` → Windows spawn 子进程 `_job` → `core/info_extractor.py: extract_info(url, options)` → `yt_dlp.YoutubeDL(opts)` → `extract_info(url, download=False)` → 全部 info/formats → Qt bridge signal → GUI。

Preview 仅覆盖 `quiet=True/no_warnings=True/skip_download=True/logger=SafeLogger`，删除 progress/postprocessor hooks 和 postprocessors；这些差异防止预览下载或加工文件。不会删除 proxy、cookiefile、cookiesfrombrowser、http_headers、username/password、usenetrc、extractor_args、socket_timeout、retries 或 impersonate。

## Download / Retry

`MainWindow._on_download` / `_retry_url` → `_build_ydl_opts` → `DownloadManager.add_task`（锁内拒绝同 URL 的 active duplicate）→ `DownloadTask.__init__` 深拷贝 options → ThreadPoolExecutor → `DownloadTask.run` → `run_ydl` → spawn `_job` → `YoutubeDL(options)` → `download([url])`。

`_job` 使用真实 yt-dlp 下载、FFmpeg merger/postprocessors；添加 after_move `VerifyOutputPP` 检查最终文件存在且非空。成功返回还要求 yt-dlp return code 为零、收到结果、子进程 exitcode=0、没有取消。100% progress 不等于 completed。simulate/skip_download 显式操作可无媒体输出，不能作为媒体下载 PASS。

## 一致性与边界

| 参数 | 当前 GUI / API 路径 | 验证 |
|---|---|---|
| proxy / geo_verification_proxy | 两阶段原样；空主代理保留为 `''` | HTTP/SOCKS5/SOCKS5H authenticated loopback 转发实际 YouTube preview 和音频下载 |
| cookiefile | 本地路径原样 | Cookie-gated 本地媒体，两阶段均通过认证 |
| cookiesfrombrowser | GUI browser string → API tuple | Chrome/Edge/Firefox 参数映射已检查；真实浏览器解密/登录 NOT TESTED |
| http_headers / User-Agent | API 可传入，GUI 无单独控件 | 受控服务验证两阶段 User-Agent 一致；敏感 header 不写持久配置 |
| username / password / usenetrc | 已有 GUI / API 传递 | 参数路径、脱敏与持久化测试；真实账号认证 NOT TESTED |
| extractor_args | GUI 无控件；API 原样保留 | 未做自定义 extractor 行为的实网验收 |
| socket_timeout / retries | API 数值转换，共同 builder | 单元测试实际 YoutubeDL 构造；实网 timeout15/retries1 |
| impersonate | GUI 无控件；API 原样保留 | 未安装额外 impersonation backend；真实行为 NOT TESTED |

不能把没有 GUI 控件的功能称作新实现；也不能把参数被保留等同于全部认证方式已实网通过。

## 取消与凭据

`DownloadTask.cancel` 设置 event；`run_ydl` 每 50ms 检查并对本任务拥有的 PID 执行 Windows `taskkill /T /F`，join 回收进程。原线程池仍负责调度，yt-dlp 本身仍负责下载。`DownloadManager.shutdown` 同时取消预览和下载，GUI closeEvent 调用 shutdown；不杀其他应用进程。

`core/credentials.py: SafeLogger/redact` 统一处理日志与异常，隐藏 URL userinfo、认证/Cookie header 和 query values。AppSettings/Presets 持久化副本删除 password/tokens、proxy userinfo、敏感 headers；运行时仍保留本次输入。Cookie 路径和 browser 名称可保存，Cookie 内容不复制进配置。history 新记录 URL 去掉凭据和敏感 query；旧 history 未批量清洗。

进程边界要求 options 可 pickle；普通 GUI 配置已验证。第三方 API 自定义不可 pickle callback/logger 不属于本次 GUI 验收范围。
