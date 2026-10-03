# B0 风险登记

基线 `0e42112dae627c10ce159ece0ef97594ccd27d39`。P0 Critical / P1 High / P2 Medium / P3 Low。没有已确认 P0；未测试项不能算安全通过。

| ID / 等级 | 问题 | 影响 | 源码位置 | 复现方式/证据 | 建议 |
|---|---|---|---|---|---|
| R01 P1 High | 预览不传下载设置 | 代理环境解析失败、私有视频缺认证，预览和实际下载不一致 | main_window.py:240 | 设置代理/Cookies 后拦截 manager.extract_info，ydl_opts=None | 两路径复用已构造参数 |
| R02 P1 High | 下载返回码忽略 | 失败可显示完成，历史不可依赖 | task.py:69–92 | Fake YoutubeDL.download 返回 1，task.status=completed | 检查结果/明确成功产物；不要使用私有 _download_retcode |
| R03 P1 High | GUI 参数未经 Python API 类型转换 | 限速与过滤器会失败，日期过滤静默无效，重试路径可能另抛异常 | settings_panel.py:673/700；ydl_opts.py:175/183；yt-dlp.yml | ratelimit=50K 为 str → TypeError；match_filter 为 list → 不可调用；http sleep=3 为 int → 不可调用；dateafter/datebefore 无 daterange | 按 API 处理 bytes、callable、DateRange、retry sleep callable，并做实际输入校验 |
| R04 P1 High | 预设应用整体默认值覆盖 | 选择画质清空代理/路径/认证，下载到错误位置、无法连接 | settings_panel.py:833/769 | 设置路径/代理后 apply_preset({'format':'ba'}) 两字段为空 | 只合并预设指定字段 |
| R05 P1 High | 明文凭据/代理密码 | 本地其它可读主体、备份/用户分享配置泄露密码 | app_settings.py:102；presets.py:62；settings_panel.py:744 | dummy 密码保存后 JSON 包含原值；Proxy echoMode=Normal | Windows Credential Manager 或不持久化密码，代理认证分开遮罩；清洗导出/预设 |
| R06 P1 High | 取消/关闭不能中断解析与 FFmpeg | UI 已关仍有工作/子进程，关闭延迟 | task.py:63/111；manager.py:107；main_window.py:317 | 静态：仅检查开始/progress Event，无 PP hook；线程池 wait=False 无进程终止；FFmpeg阶段取消未实测 | 明确取消边界，管理 Worker/Future 和子进程生命周期；加入该阶段实测 |
| R07 P2 Medium | 并发 UI 当前会话无效 | 用户设 7，实际池仍 3 | main_window.py:39/184；settings_panel.py:435 | UI=7 / manager._max_workers=3 | 明确重启要求或安全重建池 |
| R08 P2 Medium | SponsorBlock action API 错误 | 两种操作启动就抛 TypeError | ydl_opts.py:107 | SponsorBlockPP unexpected keyword action，两种都复现 | 使用真实 PP API，并配套章节/剪切 PP |
| R09 P2 Medium | metadata/chapters 并未组装 PP | 开关为真仍无嵌入 | ydl_opts.py:74 | YoutubeDL._pps['post_process']=[]，addmetadata/addchapters 不触发 CLI 装配 | 按 Python embedding API 显式构造 PP |
| R10 P2 Medium | 下载目录内写配置且非原子写 | Program Files 权限、崩溃/磁盘满损坏配置或历史 | app_settings.py:8/102；history.py:9/28；presets.py:9/62 | 源码可证；max_workers=0 合法 JSON 复现 crash，错误类型也未校验 | 用户数据目录、类型校验、原子替换、schema 迁移 |
| R11 P2 Medium | UI 每次进度全量历史写盘 | 历史大时 UI 卡顿，写放大 | main_window.py:217；history.py:51 | update_title 不论已有标题是否改变都 _save | 仅变化时写、控制频率；先测实际负载 |
| R12 P2 Medium | 活动任务可 Retry/Delete/重复 Start | 重复同目标写入、孤立下载、统计不准 | task_table.py:191/208/220；main_window.py:191/273 | 右键 Retry 无终态检查且不取消旧任务；重复 Start 无全局去重 | 活动操作约束，任务/输出路径冲突控制 |
| R13 P2 Medium | ffmpeg_location 不参与默认检测 | 有效自定义 FFmpeg 仍降级 b、错误 NOT FOUND | ffmpeg_utils.py:8/23；main_window.py:171/199 | PATH 无 ffmpeg 时 get_default_format=b；GUI检测无 opts 参数 | 统一有效位置检测，同时检查 ffprobe |
| R14 P2 Medium | Audio 预设不设 ba、preview 单选流 | 只提音频仍下载大视频；video-only 单选无声音 | presets.py:23；format_preview.py:106 | 本次 Audio MP3 实际选最高视频+音频；选流返回单 ID | 音频预设指定 ba；明确流类型与配对策略 |
| R15 P2 Medium | HTTPS 代理依赖缺失 | 官方安装不能连接 https:// proxy | pyproject.toml；settings_panel.py:400 | Urllib 唯一 handler；调用报需 requests/curl_cffi | 选定并验证代理后端；避免混淆 HTTPS目标和HTTPS代理 |
| R16 P2 Medium | 历史缺结果路径/错误/格式/原参数 | 无法可靠重试、查证最终画质或定位文件 | history.py:33；main_window.py:273 | 记录结构/Retry 用当前设置 | 最小扩展 schema 并迁移；保留任务参数快照 |
| R17 P2 Medium | 未锁依赖、无 EXE 打包/发布验证 | 升级漂移，分发和许可证未达产品门槛 | pyproject.toml；.gitignore；release 无 assets | uv sync 解析最新组合；无 build-system 警告；无 pack spec | 固定经过测试的依赖/构建、EXE与干净Win10/11验收、第三方声明 |
| R18 P2 Medium | 当前 YouTube 无 JS runtime 警告 | 一些格式可能缺失，未来提取可靠性风险 | 官方依赖安装组合 | 实际警告 No supported JavaScript runtime；本次能下载不消除风险 | 按 yt-dlp EJS 要求验证所需运行时/组件，并审计打包许可 |
| R19 P2 Medium | 日志/历史无敏感数据清洗 | token URL、异常内容可能泄露 | main_window.py:236；history.py:33；log_viewer.py:45 | 静态可能路径；未证实本次完整 Cookie/Authorization 被记录 | URL/token/代理凭据脱敏；禁止认证头日志 |
| R20 P3 Low | 内存日志/任务持续累积 | 长会话资源增长 | log_viewer.py:21；manager.py:77 | 无 maximumBlockCount；remove_finished 无 GUI 调用 | 限制日志/任务保留数量 |
| R21 P3 Low | 版本号不同步 | 用户/升级排障不准确 | pyproject.toml:3；main_window.py:314 | 3.0.0 vs About v3.1；release v3.0 | 单一版本来源 |
| R22 P3 Low | 维护样本少且无 CI | 长期稳定性证据不足 | Git history/仓库结构 | 2023后2026集中重写；0 open issues/PR 不等于无Bug | 建立核心验收后才接受底座 |

## 放行条件（建议，未实施）

先解决 R01–R06 的解析、参数、状态、预设、凭据与取消问题，再验证并发/历史/FFmpeg路径与依赖组合；最终无 Python 的 EXE 必须在干净 Windows 10/11 环境验收，并完成 LGPL/GPL 分发检查。B0 结论 CONDITIONAL GO 表示可作为小型可理解的源码起点，**不是可靠产品或发布放行**。没有进入 B0.1。
