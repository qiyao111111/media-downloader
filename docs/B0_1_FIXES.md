# B0.1 修复记录

基线 655bcb1923d412cc7737f6bcd3b3ee220546b089；分支 `codex/b0-1-core-runtime-validation`。未重写 yt-dlp 下载核心，没有新增依赖，未改 B0 报告。

| Issue | Severity | Root Cause | Files Changed | Fix | Test | Regression Result |
|---|---|---|---|---|---|---|
| Preview 忽略 Proxy/Cookies | P1 High | GUI预览未传当前下载options | gui/main_window.py, core/manager.py, core/info_extractor.py | 统一 `_build_ydl_opts`；预览仅移除下载/加工 hooks | 实际HTTP/SOCKS5/H网络转发、cookie认证；GUI捕获参数单元测试 | PASS（真实浏览器账号另列未测） |
| Python API参数类型错误 | P1 High | 直接使用CLI/YAML字符串/数字而API需要数值、callable、DateRange/PP | configs/ydl_opts.py | 大小、时间、计数严格转换；retry callable可pickle；DateRange/match_filter与实际PP | actual YoutubeDL/PP实例、n关键字重试调用、invalid值 | PASS |
| Preset 清空长期配置且音频模式残留 | P1 High | 用稀疏preset整体apply；视频preset没重置extract_audio | configs/presets.py, gui/widgets/settings_panel.py | 当前settings与preset合并；video preset明确False，audio preset用ba | GUI保留proxy/cookie/path/template/FFmpeg/subtitle，audio→video切换 | PASS |
| 凭据可能明文保存或进入诊断 | P0 Critical（已修复的风险路径） | 原持久化完整password和proxy URL；错误直接显示 | core/credentials.py, core/history.py, configs/app_settings.py, configs/presets.py, gui/widgets/log_viewer.py, gui/main_window.py, core/task.py, core/runtime.py, core/info_extractor.py | session-only password、代理认证去落盘；统一脱敏logger/error；legacy settings/presets清理；proxy控件PasswordEchoOnEdit | dummy secret配置、历史URL、header、日志脱敏检查 | PASS；旧history不批量迁移，未知自定义敏感字段不承诺全覆盖 |
| Completed误报/漏报 | P1 High | 依赖私有retcode/成功未验最终输出；Windows Pipe正常关闭109被报失败 | core/task.py, core/runtime.py | after_move检查最终文件；returncode/childexit/result/取消联合判断；EOF/OSError后仍检查结果 | 完整真实媒体成功、HTTP500、missingFFmpeg、实际FFmpeg非法参数失败 | PASS |
| Cancel无法可靠停止网络和FFmpeg | P1 High | Python线程flag只能等hook，不能终止阻塞IO/子进程 | core/runtime.py, core/task.py, core/manager.py, main.py | stdlib spawn隔离每个现有job，Windows仅终止自有PID树，join；预览exit取消；freeze_support | 8Kvideo10%/audio/真实activeFFmpeg取消、立刻重启、GUIexit、Windows PID检查 | PASS |
| 重复retry与删除行留下活动任务 | P1 High | 活动任务可重复入队且共享文件；删除未取消 | core/manager.py, core/task.py, gui/main_window.py, gui/widgets/task_table.py | 锁内activeURL拒绝重复、run只一次；active retry guard；delete先cancel | 重复队列/run单元测试，取消后同URL重新完整下载 | PASS |
| 默认无FFmpeg静默降级及坏worker配置 | P1 High | 默认可回退b；持久化非法worker0导致pool无法运行 | core/ffmpeg_utils.py, configs/app_settings.py | 默认bv+ba不设分辨率上限，FFmpeg缺失明确failed；加载类型/worker边界保护 | native571+251完整8K；missingFFmpeg失败；坏配置单元测试 | PASS |

取消状态沿用原 enum `canceled`（单l），即用户要求的 cancelled 语义；GUI/history协议不改名。终止进程保留.part由原生 yt-dlp恢复，不强删媒体文件。FFmpeg显式recode功能保留，最高画质验收未使用它。

## 失败尝试与复核

- Windows Pipe109和retry callable的`n`关键字错误均在实跑中发现并修复，最终成功与回归记录取修复后结果。
- 注入FFmpeg失败/减速参数时最初用了大写PP字典key，当前API要求小写；改为`merger+ffmpeg_o`/`merger+ffmpeg_i`后实际merger已运行且failed/cancel均证实。未把无效注入当失败验收。
- 本机FFmpeg8.0对原8K MKV/Opus probe/full-decode输出61字节Opus警告；完整下载仍不据此判8K PASS。已有remux选项无损转换MP4后，全片解码通过。默认MKV警告仍是P2，不声称已修复。
- MP4首次null sink解码出现重复DTS诊断；测试输出显式`-fps_mode passthrough -enc_time_base:v demux`保留VFR时间基准后退出0且stderr0。该设置只影响验收null输出，未修改最终文件或源FPS。

## Still Open（统一编号）

| ID | Severity | Open | B1前要求 |
|---|---|---|---|
| O1 | P1 High 验证缺口，非已证实bug | Chrome/Edge/Firefox真实cookie解密/YouTube登录、真实账号username/netrc未实测 | 使用用户明确指定测试profile/file完成至少目标认证链路验证；当前不得宣称账号验收PASS |
| O2 | P2 Medium | 本机FFmpeg8默认8K MKV/Opus有解析诊断；MP4 copy输出通过 | 制定容器/FFmpeg兼容策略；交付默认最高画质前复核，不能静默转码 |
| O3 | P2 Medium | 无启用的YouTube JS runtime；yt-dlp警告部分格式可能缺失 | 交付前配置官方支持runtime并再查真实formats；当前只对本次已返回格式负责 |
| O4 | P2 Medium | HTTPS代理server backend、impersonation、GUI代理期间计时专项未测；SOCKS两种都发domain ATYP3 | B1如承诺这些能力，补环境与测试；未加backend依赖 |
| O5 | P2 Medium | 文件持久化非atomic、旧history未迁移、worker设置需重启；状态栏FFmpeg只看PATH | B1可靠性收尾；不影响本次已验收下载 |
| O6 | P2 Medium | 独立FormatProfile/selector、最高质量产品排序、人类可读HDR/UI标签未做；8K60/HDR仅metadata | B2必修；本阶段不提前实现；不能把bv+ba原生排序称作最终产品策略 |
| O7 | P3 Low | 原有3.0/3.1版本标识不一致 | B1版本收尾 |

剩余确认P0=0；确认阻塞核心P1 bug=0；P1验证缺口=1；P2问题组=5；P3问题组=1。总体 CONDITIONAL PASS；允许准备B1，但本次按要求停在B0.1。
