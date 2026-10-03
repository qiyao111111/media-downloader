# B0.2 Browser Authentication Validation

日期：2026-10-01。基线5b0b269ce35ded388de1494a2adda6866fa3b838；新分支`codex/b0-2-browser-auth-validation`；开始时工作区干净。master及B0/B0.1分支不修改。范围仅认证修复、测试与报告，不进入B1。

**当前结论：CONDITIONAL PASS。真实Chrome/Edge登录认证缺口尚未闭合。** 原生读取失败不是登录验证PASS；Firefox读取成功但YouTube明确返回未登录。已验证两阶段参数一致、明确单一来源、文件认证、错误处理和核心回归。

## 环境与浏览器矩阵

Windows11、Python3.13.13、yt-dlp2026.8.19。实际安装Chrome154.0.8037.58、Edge154.0.4258.48、Firefox157.0。Chrome存在Default、Profile1、Profile6、Profile7；本次按要求测试Default及一个非Default Profile1。Edge有自己的Default。Firefox两个profile目录中一个有cookies.sqlite。

| Browser | Profile | Preview | Download | Result | Notes |
|---|---|---|---|---|---|
| Chrome | Default | FAIL | FAIL | FAIL | 正常打开时35进程，native报Could not copy Chrome cookie database；关闭窗口后仍有后台进程，锁未释放 |
| Chrome | Profile 1 | FAIL | FAIL | FAIL | native报Failed to decrypt with DPAPI；并非Default或Chrome路径回退 |
| Edge | Default | FAIL | FAIL | FAIL | Edge自己的User Data目录，native报Failed to decrypt with DPAPI；没有读取Chrome目录 |
| Firefox | fdqp6ei4.default-release | PASS | PASS | PARTIAL | 原生读取116个cookies，公开视频完整audio下载成功，但native auth marker=False且服务端LOGGED_IN=False；不能称登录PASS |
| Anonymous control | 无 | PASS | PASS | PASS | 无cookies，服务端LOGGED_IN=False；完整1080P下载及音轨验证 |

Edge/Firefox测试时没有运行的浏览器进程；它们的“浏览器打开状态读取”NOT TESTED。Chrome打开状态明确FAIL。锁与DPAPI为实际底层错误；不推断DPAPI失败必然由某个加密版本或账号权限导致，不修改浏览器安全设置、不自行破解数据库。

用户告知Chrome窗口已关闭后，Windows实际仍有13个chrome.exe（后续12个），同一Default复测仍报数据库无法复制。这是后台未完全退出的复测，不冒称“所有Chrome进程已关闭”。未获结束后台进程授权时不强制终止浏览器。[yt-dlp上游DPAPI问题](https://github.com/yt-dlp/yt-dlp/issues/10927)也记录此类失败；本次只据本机实际错误判定，不能把跳过解密或匿名成功当认证修复。

## 原生来源参数与一致性

使用`cookiesfrombrowser`原生API，没有导出浏览器cookies.txt或打印Cookie数据库。实际tuple结构为`(browser, profile, keyring, container)`：

```python
('chrome', 'Default', None, None)
('chrome', 'Profile 1', None, None)
('edge', 'Default', None, None)
('firefox', '<APPDATA>/Mozilla/Firefox/Profiles/fdqp6ei4.default-release', None, None)
```

GUI原有browser控件只产生`('chrome',)`等tuple（profile=None，交由yt-dlp选取）；GUI没有Profile/container选择控件，本阶段不加新UI。Default/Profile1对照使用实际项目builder的已有tuple API显式选profile。Firefox支持container tuple透传，`('firefox','test-profile',None,'none')`单元检查通过；有名container实网NOT TESTED，不虚构存在的container。

GUI共同入口`MainWindow._build_ydl_opts`→`SettingsPanel.collect_opts`→`configs.ydl_opts.build_opts`。Preview：`DownloadManager.extract_info`→`run_ydl(preview=True)`→`core.info_extractor.extract_info`→`YoutubeDL.extract_info(download=False)`。Download：`DownloadTask`深拷贝同一options→`run_ydl`→`YoutubeDL.download`。

`tests/validate_auth_flow.py`分别实际执行这两条路径；pickle后的完整options与task.ydl_opts相同，cookie source/browser/profile/proxy及headers没有阶段差异。proxy=''明确直连；browser测试无自定义header，两阶段均使用yt-dlp默认header。文件认证回归使用相同B01-test-agent，服务器确认两阶段认证和User-Agent一致。

参数一致与登录成功分开判断：即使Chrome两阶段同样failed也不能表示会话已验证。每个进程按同一profile原生加载当前cookie数据库，不冻结/复制账号凭据，因此不能声称Cookie值逐字相同；浏览器实时轮换可能改变cookie值。

## 公开页面的真实登录区分

使用公开[Big Buck Bunny watch page](https://www.youtube.com/watch?v=aqz-KE-bpKQ)，`YoutubeDL.urlopen`用原生cookiejar请求，`YoutubeIE.extract_ytcfg`只记录服务端`LOGGED_IN`布尔值。匿名False，Firefox也False；原生`YoutubeIE.is_authenticated`亦False。页面HTML、账号标识、Cookie值和Authorization没有持久化。Chrome/Edge在本地加载阶段失败，无法取得认证页对照。

未找到并验证一条“当前登录后才能稳定解析”的公开源；该补充案例NOT TESTED。没有尝试私人/付费资源或绕过访问权限。

## 单一来源与最小修复

基线`cookiesfrombrowser`与`cookiefile`可同时传入。实际yt-dlp `cookies.py:load_cookies`先读browser再读file，随后merge cookie jars；这不符合用户单一来源规则。现在共同builder遇到两者均非空明确抛出：

`Choose one Cookie source: browser OR cookies.txt; clear the other setting`

不是静默优先：没有一个来源覆盖另一个；用户清除其中一项后再执行。GUI已有Invalid Settings提示显示原因，不新增UI流程。CaseA仅file=PASS；CaseB仅browser见矩阵（Firefox可读但未登录）；CaseC明确拒绝=PASS。选项`cookiesfrombrowser='None'`不算启用browser。

另一个真实问题：当前yt-dlp对某些损坏的Netscape行会直接向stderr打印原始行并跳过，可能泄露Cookie值且静默匿名。`core.credentials.validate_cookie_file`在两阶段加载前检查文件存在、Netscape header和非注释条目结构/日期/flags；发现损坏只报行号、隐藏内容，直接failed。有效Cookie仍由yt-dlp原生解析，不重新实现cookiejar或解密。路径型Cookie文件是当前GUI的支持范围。`redact`增加SID/HSID/SAPISID/APISID/LOGIN_INFO及Secure前缀赋值的遮蔽。

## 错误与日志

| Case | Preview | Download | 子进程 | 可诊断原因 |
|---|---|---|---|---|
| 不存在browser | FAIL，无crash | failed | 0 | unsupported browser: not-a-browser |
| 不存在Edge profile | FAIL，无crash | failed | 0 | could not find edge cookies database；正确Edge目录 |
| 损坏cookies.txt | FAIL，无crash | failed | 0 | Invalid Netscape Cookie file entry at line 2; contents hidden |
| 锁定Chrome Default | FAIL，无crash | failed | 0 | Could not copy Chrome cookie database |
| DPAPI错误 | FAIL，无crash | failed | 0 | Failed to decrypt with DPAPI |

错误保留原生底层原因供GUI展示，没有降成通用Download failed。数据库锁可提示用户完全退出浏览器（后台进程也须退出）；DPAPI失败则需重新验证当前系统当前profile的原生解密能力，不能承诺关闭浏览器即可修复。

日志用SafeLogger/redact；debug不输出，未dump cookies或原始HTML。测试用dummy秘密断言不进入损坏文件异常、最终结果和日志；实际浏览器测试仅记录count/auth/server登录布尔值、profile名和安全错误。没有把SID等真实值复制到测试配置、Git或报告。

## Evidence与复现

repo外`D:\YouTube视频下载\B02 evidence`：`browser-probes.json`、`chrome-closed/browser-probes.json`、`flow/auth-flow-results.json`、`network/network-results.json`。外层日志`B02-browser-probes.log/B02-browser-closed.log/B02-auth-flow.log/B02-network.log/B02-unit.log/B02-8k-metadata.log`。只提交tests/docs和最小认证修复，Cookie fixture、媒体及日志不提交。

```powershell
.venv\Scripts\python.exe tests\validate_browser_auth.py "..\B02 evidence\probe-recheck"
.venv\Scripts\python.exe tests\validate_auth_flow.py "..\B02 evidence\flow-recheck"
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

这些显式live脚本读取当前用户profile并产生网络下载；单元测试不读取个人浏览器cookie。

## AUTH PRODUCT POLICY

2026-10-01，按用户修订的第一版认证门槛追加。本节是当前产品政策；前文测试结果、失败证据及当时门槛判断保留为历史记录，不改写为PASS。

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

第一版所需认证已有稳定、已验证路径：cookies.txt。Firefox为可选便利功能；Windows Chrome/Edge原生读取为实验性Best Effort功能，数据库锁与DPAPI/App-Bound Encryption相关平台限制不再阻塞进入B1。此产品门槛调整不代表Chrome/Edge实测通过，也不代表Firefox真实YouTube登录态已验证。

Chrome/Edge直接读取失败时，产品要求：应用不得crash，保留可诊断底层原因，并明确提示：

> 无法直接读取浏览器 Cookies。请导出 cookies.txt 后重试。

禁止绕过Windows安全机制、自行实现DPAPI/App-Bound Encryption破解、读取浏览器密码、上传Cookies或将Cookie内容写入日志。单一Cookie来源及Preview/Download认证一致性要求继续有效。

本次只追加政策文档，不实现新提示或修改运行代码；上述提示属于产品要求，不能据此宣称现有UI已显示该文案。允许进入B1，但本次完成提交后停止，不开展功能开发。
