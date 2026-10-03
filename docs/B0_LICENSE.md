# B0 许可证审计

已逐字读取仓库 `LICENSE` 原文：MIT License，`Copyright (c) 2023 Gaius Pluto`；不是仅依据 GitHub 标签判断。

| 问题 | 项目 MIT 结论 |
|---|---|
| 修改/私人使用/商业使用 | 允许 |
| 复制/重新分发/销售 | 允许 |
| 版权与许可声明 | 软件副本或重要部分必须保留版权与许可声明 |
| 修改源码必须开源 | MIT 不要求 |
| 保证与责任 | 原文包含 AS IS 免责条款 |

以上仅针对项目代码许可。分发 EXE 必须另外遵守依赖及所选 FFmpeg 构建许可证，MIT 不能覆盖它们。

| 第三方 | 需要核查的义务 | 当前结论 |
|---|---|---|
| PySide6/Qt/Shiboken | LGPL/GPL/商业许可选项；所用模块、动态替换/重新链接、许可副本与源码获取等 | 不能把整个包当 MIT；当前无 EXE，最终打包方案未审计 |
| yt-dlp | 项目 Unlicense；第三方组件与发布二进制另有许可清单 | Python 包与官方 standalone EXE 组成不同，须按实际分发产物审计 |
| PyYAML | MIT | 保留许可声明 |
| FFmpeg | 默认 LGPL，但构建选项可使 GPL/v3 或不可再分发 | 本机 ffmpeg 8.0 显式 `--enable-gpl --enable-version3 --enable-static`；不能当普通 LGPL 构建随产品任意附带 |

Qt LGPL 不当然要求自己的应用源码全部开源，但打包必须满足具体使用/替换与源码提供义务；GPL 组件选择可能改变要求。FFmpeg 作为独立程序和 GUI 的法律关系需根据最终分发设计评估；当前不能证明存在既成冲突，也不能声明产品 EXE 合规已通过。没有随仓库提供第三方 NOTICE、二进制、SBOM 或打包产物。商用发布前须固定构建与许可清单，不属于本阶段开发。

官方依据（2026-10-01 核查）：[Qt LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations)、[FFmpeg legal](https://ffmpeg.org/legal.html)、[yt-dlp license and third-party notices](https://github.com/yt-dlp/yt-dlp#license)、[PyYAML source](https://github.com/yaml/pyyaml)。本报告为工程许可核查；无法替代对具体分发物的法律审查。
