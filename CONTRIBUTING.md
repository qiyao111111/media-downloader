# 参与开发

本项目基于 Plutoeat/yt-dlp-gui（MIT），保留原作者许可。当前产品版本为 0.9.0-rc2。

## 本地开发

使用 Python 3.13 或更高版本，在仓库根目录执行：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe main.py
```

推荐 Windows x64；其他系统尚未经过完整验收。FFmpeg/FFprobe 放在 PATH 中即可供源码版使用。QuickJS 的构建与位置见 README。

## 测试

无需网络或发行产物的基础回归：

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
.venv\Scripts\python.exe -m unittest discover -s tests -p test_core_runtime.py
.venv\Scripts\python.exe -m unittest discover -s tests -p test_format_selector.py
.venv\Scripts\python.exe -m unittest discover -s tests -p test_b1_architecture.py
.venv\Scripts\python.exe -m unittest discover -s tests -p test_b3_ui.py
.venv\Scripts\python.exe -m unittest discover -s tests -p test_b4_runtime.py
.venv\Scripts\python.exe -m unittest discover -s tests -p test_b5_1_visual.py
```

完整回归使用 `python -m unittest discover -s tests -p 'test_*.py'`，其中发行包、许可清单和原生媒体测试需要先构建 Windows 产物。`tests/validate_*.py` 为人工验收辅助脚本，部分使用历史本机路径；运行前阅读脚本参数。

提交问题时附上系统版本、软件版本、复现步骤和脱敏日志。请勿提交 cookies、账号密码、下载历史或个人视频。修改应带上适当回归验证。GitHub Actions 只验证源码，不替代独立 Windows 验收或发行许可复核。
