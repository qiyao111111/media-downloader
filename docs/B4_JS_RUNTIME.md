# B4 JS Runtime

选择 **Deno 2.9.7 Windows x64**，bundled `bin/runtime/deno.exe`。
当前实际安装的 yt-dlp 原生 JS provider 已检查 Deno、Node、Bun、QuickJS 支持；
选择官方 EJS 指南优先的 Deno，且超过当前 provider 的 Deno 2.3.0 最低要求。
不引入其他 runtime fallback 或自研 JS parser。

来源和 SHA256 固定于 build/runtime-lock.json；Runtime Manager 提供绝对路径、版本和状态。
options 为 `js_runtimes={'deno':{'path':'<bundle>/bin/runtime/deno.exe'}}`；
remote_components=[]，配套 EJS 0.8.0 的 solver scripts 随包提供。
DENO_DIR 位于模式自己的 temp；不使用用户全局 Node/Deno。

## 同源 comparison

真实 source：`https://www.youtube.com/watch?v=E86EwGT_c2M`，沿用前阶段曾遇到 403/挑战的源，
没有为制造 PASS 更换视频。source worker 实际使用两个不同 JS options。

| JS | Preview | Formats count | Highest | Full 1080P download | Error |
|---|---|---:|---:|---|---|
| disabled，js_runtimes={} | PASS | 53 | 4320P | PASS，399+251 | 无下载错误；原生 no-runtime warning |
| bundled Deno 2.9.7 | PASS | 53 | 4320P | PASS，399+251 | 无；无 unsupported JS warning |

证据：[comparison.json](<D:/YouTube视频下载/B4 evidence/js-comparison-retest/comparison.json>)，
`D:\YouTube视频下载\B4-js-comparison-retest.log`，两个完整输出文件位于同一 evidence 目录。
初次 stdin 驱动因 Windows spawn 无法加载 `<stdin>` 失败，保留于 js-comparison；
修正为有 __main__ guard 的 validate_b4_js.py 后实测通过，没有把初次失败改为 PASS。

该次请求无 JS 也能成功，不能证明挑战必然被触发、格式数量增加或 403 永久解决。
结论只为 **JS runtime integration verified**。

## Frozen regression

Portable/Installed 都物理临时隐藏 bundled Deno，health 返回 NOT_INSTALLED、GUI 能启动，
同一公开视频 Preview 仍成功。操作 finally 恢复 Deno。
有 Deno 的 frozen suites 完成真实视频、音频与 proxy 请求。详情及 evidence 路径见 release report。
缺 JS 是可选能力下降，可能导致部分来源格式不完整；不阻止整个应用启动。

参考：[官方 EJS](https://github.com/yt-dlp/yt-dlp/wiki/EJS)、
[Deno Windows 安装说明](https://docs.deno.com/runtime/getting_started/installation/)。
