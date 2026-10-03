B0 RESULT: CONDITIONAL GO

# B0 源码与运行审计

该仓库可以作为可理解的小型 Python/PySide6 起点，但不是已达到长期稳定性或 EXE 发布标准的底座。此结论以先修复明确问题并补齐未测场景为条件，不能解释为生产放行。

最关键的五个依据：

1. 原始 GUI 在 Windows 11 实际启动；YouTube 完整1080P和4K视频、音视频合并、MP3提取成功，并经 ffprobe 与前5秒解码验证。
2. Core 与 Qt 通过 Signal 桥分离，网络在 ThreadPoolExecutor，结构小且可继续二开；取消/退出、重复任务、共享浅拷贝等生命周期仍不可靠。
3. 已复现预览忽略代理/Cookies、预设清空其它设置、限速/过滤/重试类型错误、SponsorBlock失败；下载返回码忽略可能误标完成。
4. 密码/认证代理明文持久化，配置/历史缺校验与原子写，下载历史没有结果路径和失败原因，尚未满足桌面产品的数据/安全要求。
5. LICENSE原文为MIT，可修改与商用；但Qt/FFmpeg分发义务、Windows EXE、Win10/干净环境、8K/HDR/真实代理与认证验证均未闭环；维护样本较少。

## 基线与范围

| 字段 | 记录 |
|---|---|
| Repository URL | https://github.com/Plutoeat/yt-dlp-gui |
| 本地完整clone | `D:\YouTube视频下载\yt-dlp-gui`；普通git clone，非shallow |
| 默认分支 | `master`，不是main；origin/HEAD → origin/master |
| 审计分支 | `codex/b0-source-audit` |
| 源码Commit | `0e42112dae627c10ce159ece0ef97594ccd27d39` |
| 最近commit（上海） | 2026-04-12 00:24:12 +08:00 |
| GitHub pushed_at | 2026-04-11T16:25:54Z（上海04-12 00:25:54） |
| GitHub updated_at | 2026-04-11T16:24:31Z（不是最后源码提交时间） |
| release | v3.0，2026-04-11T16:26:48Z，assets=[] |
| 项目版本 | pyproject 3.0.0；About显示v3.1，存在不一致 |
| 审计日期 | 2026-10-01，Asia/Shanghai |
| OS / Arch | Windows 11 专业版，10.0.26200，AMD64/x64 |
| 初始shell Python | 3.11.9；不符合项目>=3.13，未拿它冒充官方环境 |
| 实际运行Python | uv选用已安装CPython 3.13.13，.venv |
| 实际依赖 | PySide6/Essentials/Addons/Shiboken 6.11.2；PyYAML 6.0.3；yt-dlp 2026.8.19 |
| FFmpeg / ffprobe | 8.0，PATH已有Gyan essentials build；`D:\DouK-Downloader_V5.7_Windows_X64\ffmpeg-8.0-essentials_build\ffmpeg-8.0-essentials_build\bin` |

初始 git status --porcelain 空；建立指定独立分支后工作区仍干净。没有main分支被修改，master始终保持基线。所有产品源码、UI、功能均未修改，仅新增六份审计文档；测试驱动、日志、媒体放仓库外，.venv/uv.lock/运行JSON为项目已有gitignore规则忽略。

报告导航：[架构](B0_ARCHITECTURE.md)、[功能矩阵](B0_FEATURE_MATRIX.md)、[安全](B0_SECURITY.md)、[许可证](B0_LICENSE.md)、[风险](B0_RISK.md)。风险源位置均为基线行号。

## 官方运行准备与步骤

```powershell
git clone https://github.com/Plutoeat/yt-dlp-gui.git
cd yt-dlp-gui
git symbolic-ref refs/remotes/origin/HEAD
git log -1 --format=fuller
git status --porcelain
git switch -c codex/b0-source-audit
uv sync
uv run python main.py
```

执行了README推荐的uv sync，自动使用已有3.13.13并装依赖。无需安装系统FFmpeg，机器PATH已有。uv提示：项目未packaged，project.scripts入口未安装；这是源码可运行而打包不完整的证据。没有为运行重构。

实际启动检查：`.venv\Scripts\python.exe main.py`（与uv run选用的同一解释器）进程存活3秒无立即crash；独立测试驱动创建原始QApplication/MainWindow并show/processEvents，GUI_VISIBLE=True，保存并目视检查截图。窗口按钮、URL框、任务表、日志正常显示。GUI操作测试用Python调用原始slot/控件，不声称手动完成全部桌面交互。

下载测试通过原始 `build_opts → DownloadTask.run → YoutubeDL.download`，没有替换网络或下载实现；只增加超时/零重试以使网络失败有界，及仓库外输出路径/固定文件名。T7诊断mock只用于复现返回码/参数传播，不作为网络成功证据。

## 测试视频与最小验收

公开视频：[Big Buck Bunny 60fps 4K - Official Blender Foundation Short Film](https://www.youtube.com/watch?v=aqz-KE-bpKQ)，id `aqz-KE-bpKQ`，duration metadata=635s。实际metadata的license为 `Creative Commons Attribution license (reuse allowed)`，用于下载与处理测试，不重新发布媒体。输出目录 `D:\YouTube视频下载\B0 运行测试 中文` 含中文与空格。

| Test | 输入/调用 | 实际结果 | 状态/边界 |
|---|---|---|---|
| T0 GUI/metadata | 原始main启动；原始core.extract_info；build_opts默认参数 | GUI不立即crash；读取标题、53个formats、thumbnail URL | GUI/metadata PASS；界面未实现封面显示；未验证thumbnail图片下载 |
| T1 1080P | 原始1080p预设，输出MP4 | 399：height1080/vcodec av01.0.09M.08/acodec none；251：height null/vcodec none/acodec opus；合并134657121 bytes | ffprobe AV1 1920×1080 + Opus，634.601s；前5秒解码exit0 |
| T2 4K | 自定义 `bv[height=2160]+ba`，merge_output_format=mkv | 401：height2160/vcodec av01.0.13M.08/acodec none；251 audio-only Opus；合并722514488 bytes | ffprobe AV1 3840×2160 + Opus，634.608s；前5秒解码exit0；不是只看文件名 |
| T3 Audio | 原始Audio MP3预设 | 最终MP3 19037493 bytes，634.578146s；前5秒解码exit0 | 提取成功，但实际先选401+251下载4K视频，不能算纯音频流下载PASS |
| T4 Resume | T1下载中强制结束运行原始DownloadTask的Python进程，再启动同参数程序 | `.part`保留；日志 `Resuming download at byte 65622351`；最后完成T1 | 核心进程硬中断续传PASS；不是GUI队列自动恢复；需相同format/路径 |
| T5 WebM | T1产物用FFmpeg无损拆出5秒video/audio，yt-dlp FFmpegMergerPP执行WebM合并 | AV1 video + Opus audio；完整5秒解码exit0 | 本地PP容器验证PASS；GUI全片WebM下载未测，矩阵PARTIAL |
| T6 Cancel | 原始720P DownloadTask，进度超过1MiB请求cancel | 下一hook终止，status=canceled，.part=4193280 bytes | 下载阶段有效；metadata/FFmpeg取消不是立即可控 |
| T7 缺陷诊断 | GUI参数/持久化、实际yt-dlp API + 少量mock | 详见下表 | 每项有明确复现，不是推断 |
| T8 Windows路径 | 中文+空格实际源码/输出路径，prepare_filename含中文及 `:*?"<>|` | 下载/合并成功；标题禁止字符转安全字符 | 中文路径PASS；中文用户名、长路径、完整Unicode basename未测 |
| T9 HTTPS proxy | 默认uv环境YoutubeDL(proxy=https://127.0.0.1:9).urlopen | NoSupportingHandlers；要求requests/curl_cffi | https://代理FAIL；未添加依赖掩盖问题 |
| T10 持久化/队列/认证传参 | 临时历史文件add/update后重建DownloadHistory；mock Worker在max_workers=2下提交5任务；空Netscape jar及代理/browser字段转换 | HISTORY_RELOAD_PASS；峰值活动Worker=2；COOKIE_EMPTY_JAR_AND_PROXY_MAPPING_PASS | 队列控制与文件重载通过；mock不算真实视频并发测试，空jar不算登录验证 |

ffprobe首次由测试驱动 `text=True` 按本机GBK解码JSON，遇Unicode标签发生测试读取错误；FFprobe本身exit0。随后改为读取bytes并UTF-8 decode，重新核实全部三文件的streams/duration，以上结果来自修正后的读取。该错误属于审计驱动，不记为项目bug。媒体可由FFmpeg软件解码，**没有断言Windows自带播放器支持AV1/Opus/MKV**。

## 已复现缺陷摘要

| 诊断 | 原样结果 |
|---|---|
| 设置代理/Edge Cookies后调用List Formats | 传给manager的ydl_opts=None |
| GUI并发改7 | UI=7，manager._max_workers=3 |
| 路径/代理设置后apply_preset({'format':'ba'}) | path/proxy均为空 |
| dummy密码保存到临时AppSettings | 明文JSON包含AUDIT_DUMMY；未保存真实凭据 |
| 合法配置max_workers=0 | ValueError: max_workers must be greater than 0 |
| mock download返回1 | DownloadTask.status=completed |
| SponsorBlock mark/remove | TypeError: unexpected keyword argument 'action' |
| ratelimit=50K的实际slow_down | TypeError：float与str无法比较 |
| match_filter=duration>60的实际_match_entry | TypeError: 'list' object is not callable |
| YAML http retry sleep | 类型int，非callable；调用TypeError；默认重试分支使用该函数 |
| embed_metadata/chapters=True | YoutubeDL._pps['post_process']=[]，未注册FFmpegMetadataPP |
| PATH找不到FFmpeg | default format=b，即使设置自定义位置也不参与该检测 |

## 断点续传/覆盖/重试

build_opts默认continuedl=True；未设nopart，yt-dlp下载器正常使用.part，T4已实证。GUI没有continue/no-overwrites/retries/fragment retries字段，没有主动提供覆盖策略；下载器默认处理existing file，不可据此保证多任务不会同路径写。项目没有CLI解析层，retries/fragment_retries未显式设为CLI常见10，不能套用CLI默认值作为应用保证。YAML `retry_sleep_functions.http:3`不符合API callable要求，故异常重试路径有风险。本次下载测试显式retries/fragment_retries/extractor_retries=0；恢复测试不依赖重试。

## 依赖与维护核查

| 依赖 | pyproject要求 | 安装版本 | 用途/维护状态 |
|---|---|---|---|
| PySide6 | >=6.11.0 | 6.11.2 | GUI；官方Qt维护，PyPI 2026-08-18有发布；本机主要API运行正常 |
| yt-dlp | >=2026.3.17 | 2026.8.19 | extraction/download/PP；上游release 2026-08-19，仍维护；项目有API映射错误与私有属性使用 |
| PyYAML | >=6.0.3 | 6.0.3 | safe_load默认参数；上游release 2025-09-25，未发现废弃迹象 |
| Shiboken6 / PySide6 Essentials/Addons | PySide6传递依赖 | 6.11.2 | Qt bindings/runtime；包含分发许可义务 |
| requests / httpx | 未声明/未安装 | 无 | 本项目没有直接HTTP代码；缺requests/curl_cffi使HTTPS代理不可用 |
| FFmpeg/ffprobe | README外部工具，无包依赖 | 8.0 | yt-dlp PP调用，本机PATH；不内置，不自动下载 |

依赖不锁，uv.lock被忽略；没有requirements.txt/setup.py/build-system/打包spec/CI。当前PySide6不是旧PyQt5/Qt5迁移底座，Qt API未见本次立即不兼容；不能以此替代Win10和长会话测试。

上游本项目最近commit为2026-04-12，最近release为v3.0同日；GitHub API本次返回open issues=0、open PR=0；2023后长期间隔，2026集中GUI重写。没有发现大量未解决严重Bug的公开issue，但代码实证已发现多项问题，低issue数量不是稳定性证据。YouTube实际警告缺JS runtime、无JS runtime extraction已deprecated，部分formats可能缺失；当前下载成功仍需后续验证EJS依赖与打包。

维护来源：[项目仓库](https://github.com/Plutoeat/yt-dlp-gui)、[v3.0 release](https://github.com/Plutoeat/yt-dlp-gui/releases/tag/v3.0)、[yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases)、[PySide6 PyPI](https://pypi.org/project/PySide6/)、[PyYAML release](https://github.com/yaml/pyyaml/releases/tag/6.0.3)。

## 可重复检查与证据位置

本机仓库外保留：`D:\YouTube视频下载\b0_runtime.py`、`b0_download.py`、`b0_more.py`、`b0_final_checks.py`、`b0_persistence_queue.py`；日志 `b0-runtime.log`、`b0-download.log`、`b0-resume-download.log`、`b0-final-checks.log`、`b0-persistence-queue.log`；截图 `b0-gui.png`；三个完整媒体及本地5秒样本在上述测试目录。原始metadata JSON有临时签名stream URLs，未提交到git，报告只保留format标识/编解码等摘要。审计驱动不是产品功能，也未进入源码分支。

最小无需网络的可重复检查（在仓库根目录用.venv解释器执行；当前基线应暴露两个缺陷，修复后应改变结果）：

```python
from unittest.mock import patch
from core.task import DownloadTask
from configs.ydl_opts import build_opts
class YDL:
    def __init__(self, opts): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def download(self, urls): return 1
with patch('core.task.yt_dlp.YoutubeDL', YDL):
    t = DownloadTask('https://example.invalid', {})
    t.run()
    assert t.status.value == 'completed'  # confirms R02 at audit baseline
assert isinstance(build_opts({'match_filter': 'duration>60'})['match_filter'], list)
```

## 未验证边界与停止点

没有测试真实Cookie解密/登录、HTTP/SOCKS认证代理、完整playlist、8K/HDR、Win10、中文用户名、超长路径/emoji basename、网络故障重试、FFmpeg阶段即时取消、多任务争用与压力、干净机器EXE及完整依赖漏洞/抓包审计。功能矩阵逐项标记，不将“依赖支持”当成实测PASS。

已完成源码审计、架构分析、运行验证、风险识别和二开评估；没有修复、重构、UI变更、删除或新增产品功能，没有进入B0.1。提交只含六份B0文档。最终审计commit由git输出（不把文档内自引用hash混同源码基线）。
