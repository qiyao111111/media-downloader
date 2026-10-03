# B4 Packaging

## Bundle / installer

PyInstaller **6.22.3 onedir**；正式 spec 是 build/MediaDownloader.spec。
main.py 为入口；collect_all 收集 yt_dlp/EJS hidden imports 和 solver datas，copy_metadata
支持版本检测；YAML/styles/icon 为只读 assets。FFmpeg shared DLLs 与 Deno 在根 bin，
Qt/Python shared libraries 在 _internal。没有 onefile 首启解包。

统一版本 app/version.py = 0.9.0rc1，Windows numeric version=0.9.0.1。
EXE ProductName/FileDescription/CompanyName/Copyright/版本资源和临时 ICO 已生成；
Installer 使用同源版本。实际卸载注册表、EXE version=0.9.0rc1，Publisher=
Media Downloader Contributors。图标使用 ICO 16/32/48/256，EXE/Setup 引用，快捷方式默认继承 EXE。
此项验证是资源/入口和正常 GUI 启动检查，未做独立人工截图验收。

Inno Setup **6.7.3**：默认 current-user，无 UAC；用户主动选 all-users 才到 Program Files
并请求提升。正常运行不需要管理员。声明 minimum Windows 10 22H2 x64；Win10 未实测。
当前非管理员宿主测试安装到 `D:\下载测试\YouTube视频\B4 Installed 验证`。
开始菜单、可选桌面快捷方式、卸载项均真实创建并在卸载时删除；视频/LOCALAPPDATA 配置保留。
Program Files all-users 安装 NOT TESTED，当前环境不提升权限。
不修改 PATH/系统代理/浏览器，不装驱动或插件，无遥测/上传。

Portable 有 marker，config/data/logs/temp 在 EXE 旁；安装版写 LOCALAPPDATA。
默认视频在用户 Downloads，指定目录可在程序外。Portable 目录删除测试因自动审批审查
拒绝递归删除（blocked by policy）为 NOT TESTED，测试副本保留；无 active process。

## Resolved packaging failure

初次 frozen QtWidgets 导入报找不到指定程序。启动安全日志定位到 PyInstaller 从开发机
PATH 收集了 Poppler 的 ICU 78 DLL，Qt 需要 Windows 系统 ICU 的接口。
构建 PATH 隔离 + spec 排除 icuuc/icuin/icudt，重新 clean build 后正常启动。
Windows ICU 是 OS 组件，非用户安装的 Python/FFmpeg 依赖；Win10 的实际兼容性未验证。

QtGui 广泛 hook 还会带入未使用的 QtPdf/QtVirtualKeyboard 和 QML/Quick。
spec 排除这些模块与插件，当前只含 Core/Gui/Network/OpenGL/Svg/Widgets Qt 库。
避免无需求 GPL-only 组件和额外体积。没有改变应用 UI 功能。

## Licenses / provenance

release/THIRD_PARTY_NOTICES.txt 和 release/LICENSES 是实际生成产物。
包内同样提供 licenses/。保留原项目 MIT 版权文本、yt-dlp/EJS distribution licenses、
PySide6/Shiboken wheel license files、Qt LGPLv3/GPLv3 texts、PyYAML MIT、Python LICENSE、
PyInstaller GPL bootloader exception 和 Deno 2.9.7 直接 MIT license。
这些声明来自实际包/对应 tag，不把商业授权文本当作已购买的商业 license。

FFmpeg 来源为 BtbN dated release `autobuild-2026-10-01-13-06` 的
`ffmpeg-n8.1-latest-win64-lgpl-shared-8.1.zip`；digest 和来源保存在 runtime-provenance.json。
ffmpeg/ffprobe 动态输出 `n8.1.3-14-g330caae0c1-20261001`。
实际 configuration 含 --enable-version3 --enable-shared --disable-static，
没有 --enable-gpl / --enable-nonfree，archive LICENSE.txt 为 LGPLv3；它与先前开发机 Gyan GPL build 不同。
所有原始 bin shared libraries 随包保留，允许用户替换/调试相应未修改库。
该 LGPL build 没有 libx264/libx265；显式视频重编码已在 B1 Defer，B4 不增加转码能力。
merge/remux/source quality 和 MP3 audio extraction 已真实验证，不通过转码/upscale 制造画质。

**公开转发行审查仍未关闭（P1）**：需要完整确认 FFmpeg/Qt 对应源码提供安排、外部
依赖 notices，以及 Deno 内嵌 V8/Rust 等传递组件所需声明。直接 license 和 source links
不等于已证明全量合规。当前仅创建本地未发布 RC，不声称法律合规 PASS。
NOTICE 明确标记 Deno transitive notices 待审，不虚构已经保留。

主要依据：[FFmpeg legal](https://ffmpeg.org/legal.html)、
[Qt LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations)、
[对应 FFmpeg 构建源](https://github.com/BtbN/FFmpeg-Builds/tree/autobuild-2026-10-01-13-06)、
[Deno tag](https://github.com/denoland/deno/tree/v2.9.7)。

## Artifacts

| File | Bytes | SHA256 |
|---|---:|---|
| MediaDownloader-Portable.zip | 170181198 | a1f0d6d71a2199d608e18adbb58adcd6911c3250a643ee6bab03522a64fe83b1 |
| MediaDownloader-Setup.exe | 123475281 | d440b56fdeb4a89d5da4dd053fd5052721a9c02172576dedc217e307a4dc60bd |

真实 Get-FileHash 与 checksums.txt 一致。Setup Authenticode = NotSigned；未购买/伪造证书。
Windows Defender 本地 custom scan 完成，无 threat detection 条目；没有上传 VirusTotal。
这不是对其他杀软或其他机器无误报的承诺。
