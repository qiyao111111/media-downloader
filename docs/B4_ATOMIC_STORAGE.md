# B4 Atomic Storage

Settings、History 和用户 Presets 共用 `services/atomic_storage.py`；保留 JSON 格式和既有服务。
没有迁移数据库。schema/type 校验仍由对应服务完成，密码和敏感 headers 不被持久化。

## Write / recovery

1. UTF-8 JSON 在触碰既有文件前序列化；失败保留原文件。
2. 既有文件可解析时，经服务 sanitizer 清理，再用同目录 tempfile/flush/fsync/replace
   保存最后有效版本到 `.bak`。不会让旧配置中的密码进入新 backup。
3. 新 JSON 写同目录唯一 `<name>.<random>.tmp`，flush + fsync，关闭 handle，再 os.replace。
4. finally 删除剩余临时文件。写/同步/替换失败抛出可诊断 OSError，原文件保留。

读取：主文件 -> 合法 `.bak` -> defaults；损坏、空文件、错误类型、Unicode 解码/IO 失败
不会令加载 crash。不读取任意 `.tmp`。主文件已损坏时保存新数据不覆盖已有有效备份。
备份是上次有效版本，恢复可能丢失最后一次未成功保存的设置/历史条目。

同目录替换避免跨卷移动；fsync 已实测调用。此方案不承诺硬件/文件系统在所有断电情形下
绝对持久，也不解决两个独立应用实例同时写同一配置的 last-writer-wins 问题。
应用默认单个服务串行保存，B4 没有新增多进程数据库/锁服务。

## Checks

| Requested case | Evidence / result |
|---|---|
| 正常 settings/history 写入 | test_atomic_settings / test_atomic_history PASS |
| 写入中异常 | fsync failure、replace failure、serialization failure，旧主文件保留 PASS |
| JSON 损坏 | settings/history 从 .bak 恢复 PASS |
| 临时文件存在 | .tmp 不被当成正式文件 PASS |
| backup 存在/主文件缺失 | 恢复 backup PASS |
| 空文件 | defaults PASS |
| Unicode | 中文键、值、路径及 history title UTF-8 PASS |
| corrupt primary 不污染 backup | PASS |
| presets / legacy credential backups | PASS，旧 SECRET 不在主文件或 backup 中 |

以上为 test_b4_runtime.py 的可执行检查，包含在 135 PASS 中。
Portable 和 Installed 的实际 frozen GUI 保存 retries=7、workers=1 和中文下载目录，
退出并重启后设置保持，history 数量保持。分别强制终止两次已显示主窗口的空闲 EXE，
再启动后 Settings/History JSON 可读，历史状态全部 terminal，历史不自动重新排队。
不是断电实验，也没有宣称强杀活跃下载时操作系统必然清理所有后代。
活跃下载的正常退出 warning/cancel/worker cleanup 另有真实 frozen 实测。

证据目录：`D:\YouTube视频下载\B4 evidence\portable-lifecycle`、`installed-lifecycle-retest`。
初次长路径 fixture 含 Windows 不支持的尾随空格，启动 mkdir 失败；保留失败日志，
修正测试路径组成后通过，生产路径逻辑没有为测试另开分支。
