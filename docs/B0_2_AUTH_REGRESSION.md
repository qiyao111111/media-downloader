# B0.2 Auth Regression

2026-10-01，基线5b0b269ce35ded388de1494a2adda6866fa3b838。报告状态按实际结果记录；B0.2当前CONDITIONAL PASS且**不能正式进入B1**：Chrome/Edge原生认证仍失败，真实登录会话未验证。详见B0_2_BROWSER_AUTH。

| Test | Status | Evidence / 限制 |
|---|---|---|
| Anonymous Preview | PASS | 无Cookie metadata成功，公开watch页LOGGED_IN=False |
| Anonymous Download / 1080P | PASS | E86EwGT_c2M完整399 AV1视频+251 Opus音频→MP4；1920×1080，文件47913467bytes，两流ffprobe；10秒decode0/stderr0 |
| Cookie File Preview | PASS | Netscape受控Cookie，两阶段相同source；cookie-gated本地服务实际认证True |
| Cookie File Download | PASS | 完整媒体completed；User-Agent一致；child0 |
| Browser-only Chrome Default | FAIL | 锁定数据库，Preview/Download相同底层原因；无crash |
| Browser-only Chrome Profile1 | FAIL | DPAPI解密失败，两阶段failed |
| Browser-only Edge Default | FAIL | DPAPI解密失败，使用Edge目录 |
| Browser-only Firefox | PARTIAL | 原生cookie读取/两阶段公开视频PASS，但服务端False，登录session未验证 |
| 文件+浏览器同时配置 | PASS | 统一builder明确拒绝双来源，不静默合并；GUIInvalid Settings可诊断 |
| Browser Profile tuple | PASS | 四项tuple保留；实际Default/Profile1分别执行；GUI自定义profile控件未实现 |
| Firefox container tuple | PASS | 原有API透传`('firefox','test-profile',None,'none')`；真实有名container未测 |
| Preview/Download options一致性 | PASS | 实际run_ydl Preview和DownloadTask options snapshot一致，source/browser/profile/proxy相同 |
| HTTP Proxy | PASS | authenticated loopback真实YouTube preview3/download6、CDNTrue、completed、child0；port12605 |
| SOCKS5 Proxy | PASS | 实际preview3/download4、认证True、CDNTrue、child0；port8644 |
| SOCKS5H补充 | PASS | 实际preview3/download6、认证True、CDNTrue、child0；port2119 |
| Invalid browser | PASS | 测试输入not-a-browser：Preview报错而不crash，Downloadfailed，child0，unsupported browser可诊断 |
| Invalid profile | PASS | Edge不存在profile：Preview报错，Downloadfailed，child0，正确Edge路径 |
| Corrupt cookies.txt | PASS | native加载前安全拒绝损坏行；两阶段failed，不输出dummy SID内容 |
| Credential Logging | PASS（已测路径） | SafeLogger忽略debug、mask认证header/query/SID类赋值；未输出实际Cookie内容/数据库/HTML；dummy秘密检查 |
| 8K metadata / format extraction | PASS | builder有改动所以复测；真实571=7680×4320 fps30 AV1视频+251 Opus，不重新下载全片 |
| 8K full download / decode | NOT TESTED（本阶段） | 保留B0.1真实PASS历史，本阶段按要求只复测metadata |
| Unit regression | PASS | stdlib unittest10项；file验证、冲突拒绝、参数透传、安全、preset及原B0.1核心测试 |
| Compile / diff check | PASS | compileall和git diff --check |
| 登录后可区分服务端响应 | PARTIAL | 匿名False和FirefoxFalse是实际结果；Chrome/Edge加载失败不能取登录对照 |
| 登录必需的公开视频 | NOT TESTED | 未验证合适源；不绕过私人资源权限 |

## 最小修改及影响

- `configs/ydl_opts.py`：两种Cookie source同时设置时明确拒绝；其他格式/代理/超时参数不改。
- `core/credentials.py`：Cookie文件加载前安全校验，以及常见SID类诊断脱敏。
- `core/info_extractor.py/core/runtime.py`：两阶段在native Cookiefile解析前调用同一校验，避免原始坏行进入stderr。
- `tests/test_core_runtime.py`：源冲突、container tuple、坏文件保密测试；原mock参数流测试显式mock文件校验，GUIpreset测试先断言双来源拒绝再清除file测试browser-only。
- 新live脚本`validate_browser_auth.py/validate_auth_flow.py`仅显式运行时读取浏览器profile；不安装软件或账号系统。

## Still Open

1. Chrome Default后台持有Cookie库；完全退出后需重测。关闭窗口不等于没有后台进程。
2. Chrome Profile1/Edge Default原生DPAPI失败；保留底层原因，没有解密绕行或降为匿名成功。
3. Firefox profile实际未登录YouTube；“读取浏览器Cookie成功”不等于“使用有效登录会话成功”。
4. Chrome或Edge真实登录态的Preview/Download验收必须补齐，**B1门槛仍未通过**。
5. GUI无显式profile/container选择控件；本阶段通过已有tuple API验证，不新增UI。

Git边界：master/B0/B0.1引用保持原值；只在新B0.2分支提交认证相关改动、测试和两份报告。没有产品开发、Format Selector或UI重构。

## AUTH PRODUCT POLICY

2026-10-01，按用户修订的第一版认证门槛追加。前文回归矩阵和Still Open保留为历史实测及当时门槛判断；当前产品门槛以本节为准。

```text
B0.2 Runtime Result = CONDITIONAL PASS
Product Gate = PASS FOR B1
```

| Authentication Source | First-release Policy |
|---|---|
| cookies.txt | SUPPORTED |
| Firefox browser cookies | BEST EFFORT |
| Chrome browser cookies on Windows | EXPERIMENTAL |
| Edge browser cookies on Windows | EXPERIMENTAL |

cookies.txt是第一版正式支持的稳定、已验证认证路径。Firefox可选；Windows Chrome/Edge原生读取是非核心便利功能，数据库锁和DPAPI/App-Bound Encryption相关平台限制不再作为进入B1的阻塞条件。Chrome/Edge原测试FAIL与Firefox登录验证缺口仍保留，不因政策调整改为PASS。

Chrome/Edge直接读取失败时，产品要求应用不crash，并提示：

> 无法直接读取浏览器 Cookies。请导出 cookies.txt 后重试。

底层错误须保持可诊断；不得绕过Windows安全机制、自行实现DPAPI/App-Bound Encryption破解、读取浏览器密码、上传Cookies或把Cookie内容写入日志。一次任务只使用一种Cookie来源，Preview/Download继续使用相同认证链路。

本次变更仅为文档追加，无新运行测试、无代码或UI修改；提示文案是产品要求而非已实现声明。Product Gate通过不改变历史Runtime Result，也不启动B1功能开发。
