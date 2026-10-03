# Windows EXE 签名与 SmartScreen

当前 GitHub 一键包为 **未签名**。代码签名尚未完成，不能宣称 SmartScreen 提示已解决。

微软同时评估签名身份和文件信誉。可信 OV/EV 或云签名可显示验证过的发布者并积累信誉，但新文件仍可能有提示。自签名、改名或重新打包不能代替可信签名。不要要求普通用户关闭 SmartScreen 或安装项目自己的根证书。

官方依据：[SmartScreen reputation](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation)、[代码签名选项](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options)、[SignTool](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool)。

## GitHub 下载 EXE 的接入流程

1. 获得经过身份验证的可信代码签名证书或签名服务。
2. 完成 Windows payload 构建，保留许可证及对应源码材料。
3. 先签名主程序，再重新生成包含该主程序的一键包，最后签名外层 EXE。签名后不能修改文件，校验和必须重新生成。
4. 复测实际启动、运行环境和签名；发布新的版本并持续使用同一发布身份。

本仓库 `sign_windows.ps1` 接入 Windows 当前用户证书存储区的证书，可用于硬件令牌/兼容签名提供商。需要 Windows SDK 的 SignTool、Inno Setup 编译器和可访问的私钥；不需要导出私钥或把密码写入仓库。

```powershell
.\sign_windows.ps1 -Thumbprint <证书指纹> -SignTool <signtool.exe路径> -InnoCompiler <ISCC.exe路径> -CheckOnly
.\sign_windows.ps1 -Thumbprint <证书指纹> -SignTool <signtool.exe路径> -InnoCompiler <ISCC.exe路径>
python tests/validate_easy.py
```

这条签名执行路径尚未在真实证书下运行：当前开发机没有代码签名证书。云签名服务需要接入其专用接口，不能直接使用此证书存储区脚本。

## 免费开源签名渠道

[SignPath Foundation](https://signpath.org/apply) 接受符合条件的开源项目申请。免费名额需要审核；新项目不保证获批。该服务要求可验证的源码到二进制构建流程、维护者 MFA、签名批准角色、签名策略以及卸载说明。当前仓库仍需完成对应准备，不能把本地上传的候选包称为已通过 SignPath 审核或已经签名。

申请时可提供：项目 `qiyao111111/media-downloader`，MIT 许可，Windows 桌面视频下载器，维护账号 `qiyao111111`，GitHub 发布链接及源码。账户创建、联系方式、审核和条款接受由维护者完成；没有授权前不代发申请。

## 删除一键版

关闭应用后删除 `%LOCALAPPDATA%\MediaDownloader-Easy` 即可删除应用文件。设置和历史位于 `%LOCALAPPDATA%\MediaDownloader`，如需清除需自行备份后删除；已下载视频默认在 `Downloads\MediaDownloader`，不会自动删除。
