# B1 Task Policy

`core.manager.DownloadManager`继续使用ThreadPoolExecutor调度，`core.runtime.run_ydl`继续spawn每个native job。GUI main thread只读输入/展示/发命令/收Qt signals。

| Operation | Policy |
|---|---|
| Add Task | 锁内按完整URL字符串检查非terminal重复；拒绝重复，不创建第二worker |
| Queue | 新任务queued，现有executor控制并发；任务记录先入manager再submit |
| Preview | 同一builder与认证/网络options；executor内worker，不在GUI执行网络 |
| Cancel | queued可即时终态；active待拥有的进程树停止；不误杀无关进程 |
| Remove Task | cancel先行；terminal从manager清除；active仍追踪直到取消结束，remove_finished清理 |
| Retry Task | 只允许terminal；新ID、保留旧.part由yt-dlp恢复；历史任务可由URL新建 |
| Completed/Failed/Cancelled URL | 可由用户新建任务，不恢复原任务状态 |
| Concurrent Downloads | max_workers1..10；空闲时configure_workers更换pool；活任务时明确拒绝改数 |
| Concurrent Fragments | 独立concurrent_fragment_downloads交yt-dlp，与pool数量不混用 |
| Exit | cancel_all及preview event；Windows进程join；GUI历史标cancelled，移除logging handler |

精准URL字符串去重沿用B0.1；不新增“canonical URL”猜测，避免playlist/query语义丢失。以后若要video-ID去重须明确产品规则。B1未实现永久队列或数据库调度。

Qt事件：task_added/task_updated/task_progress/task_completed/task_failed/task_cancelled；DownloadBridge另保留旧progress/status_changed/error接口与typed_error。callbacks是纯Python，Qt bridge跨线程emit。真实产品无QTimer轮询任务；test QTimer仅监测响应与自动烟测。

Retry UI只有成功建立新任务后移除旧行/旧history，参数校验失败不会先丢旧记录。删除当前行先cancel worker。逐条task模型/history只表示job级结果；Playlist多条final files仍在DownloadTask.output_files列表，output_path代表首个输出，完整playlist历史展开延后。

安全：task options深拷贝用于当次会话，密码不落盘；history只存允许字段，diagnostics脱敏。没有shell=True/eval/exec/日志上传/telemetry。FFmpeg调用由native PP或安全argument-list工具helper执行，不拼shell。
