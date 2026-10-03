# B4 Build Guide

2026-10-02，Windows 11 Pro 10.0.26200 / AMD64；版本 `0.9.0rc1`，未签名的本地 RC 构建。
分支从干净的 B3 `11b723a1daeb6dc82e3705c2955f8beb2cddc984` 创建为
`codex/b4-runtime-packaging`。分支 reflog 确认起点；没有修改 master、B1、B2、B3 分支。

## 构建环境

| Component | Version / source |
|---|---|
| CPython | 3.13.13 x64 |
| PyInstaller / hooks | 6.22.3 / 2026.8 |
| PySide6 / Qt / Shiboken | 6.11.2 |
| PyYAML | 6.0.3 |
| yt-dlp / matching EJS | 2026.8.19 / 0.8.0 |
| Inno Setup | 6.7.3，构建机工具，不随产品安装 |
| FFmpeg / FFprobe | BtbN n8.1.3-14-g330caae0c1-20261001，shared LGPLv3 |
| Deno | 2.9.7 Windows x64 |

`requirements-lock.txt` 固定直接运行依赖、构建依赖及它们所需的构建辅助包。
`build/runtime-lock.json` 固定三个官方 release 下载 URL 和 SHA256。
不是开发机全部包的 pip freeze；未使用 Node/Bun 或第二套打包系统。

## 命令

在项目根目录，准备 CPython 3.13.13 x64、虚拟环境、固定依赖和 Inno Setup 6.7.3：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe build_windows.py
```

当前宿主虚拟环境不含 pip，实测依赖安装方式是
`uv pip install --python .venv\Scripts\python.exe -r requirements-lock.txt`。
两种方式安装同一个 lock；终端用户不需要这些构建工具。
ISCC 从构建机 PATH 或 `.tools/inno/ISCC.exe` 获取。不要以管理员身份运行应用。

脚本检查 archive SHA256，下载先写临时文件，校验成功才替换缓存；校验失败保留旧缓存。
自动生成临时 ICO 和统一版本资源，调用正式 spec，复制完整 FFmpeg shared bin、Deno、
许可证与 README，输出 Portable ZIP，再调用 Inno Setup 输出安装器、checksum 和 manifest。
首次构建需要网络；产品首次启动不下载运行时。

清理只针对已解析并确认在 repo 内的 `build/work`、两个生成 bundle、`dist/release`
和 `.tools/ffmpeg` 解压目录；保留 source/docs、下载 archive 缓存及用户数据。
生成 ICO/version 文件留在被忽略的 build 子目录，正式 spec/脚本/lock 被 Git 跟踪。

## 输出和复现边界

```text
dist/MediaDownloader/                 installed payload
dist/MediaDownloader-Portable/        portable.flag + same payload
dist/release/MediaDownloader-Portable.zip
dist/release/MediaDownloader-Setup.exe
dist/release/checksums.txt
dist/release/THIRD_PARTY_NOTICES.txt
dist/release/LICENSES/
dist/release/build-manifest.json
```

最终日志：`D:\YouTube视频下载\B4-build-final.log`。PyInstaller 与 Inno 均成功，
最后 Inno 编译耗时 85.594 秒。构建时 PATH 隔离为 Python 基础目录和 Windows 系统目录，
删除 PYTHONPATH / QT_PLUGIN_PATH / QML2_IMPORT_PATH 环境覆盖。

固定版本和输入可重复构建；不承诺 ZIP 时间戳、PE 时间戳或压缩器输出字节完全一致。
最后一次 notices-only 构建已逐个比较 PyInstaller 内嵌 archive member 与所有 bin 文件，
代码和原生运行时与完整回归版本逐字节相同。见 `B4_RELEASE_VALIDATION.md`。

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
```

结果：105 旧测试 + 30 B4 测试 = 135 PASS，无 skip。
宿主 fixture 驱动脚本在 tests/validate_b4_*.py；它们的 Python/HTTP server 是测试设施，
目标 frozen EXE 子进程始终使用只有 Windows 系统目录的 PATH。

Clean Machine、Windows 10、中文 Windows 用户名均 NOT TESTED。
完整第三方转发行 notice/对应源码义务仍待复核；当前产物未对外发布，不能据此宣称正式 release。
