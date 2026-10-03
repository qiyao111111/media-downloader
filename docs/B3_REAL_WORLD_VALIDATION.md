# B3 Real World Validation

Date: 2026-10-02, Windows, Python 3.13.13, PySide6 6.11.2,
yt-dlp 2026.8.19, FFmpeg/FFprobe 8.0. Tests instantiate the real MainWindow and
operate Qt controls/signals with the real Manager/isolated runtime. Temporary
settings/history and consent responses are harness-controlled. Source extraction,
download and FFmpeg processing are not mocked. Cookies/proxies use controlled
fixtures, not recorded personal credentials.

## Evidence locations and repeatable checks

Evidence is outside Git: `D:\YouTube视频下载\B3 evidence\`.
Media: `D:\下载测试\YouTube视频\B3验证\`.

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tests/validate_b3_desktop.py 'D:\YouTube视频下载\B3 evidence\desktop'
.venv\Scripts\python.exe tests/validate_b3_desktop.py 'D:\YouTube视频下载\B3 evidence\4k-retest' 4k-resume
.venv\Scripts\python.exe tests/validate_b3_desktop.py 'D:\YouTube视频下载\B3 evidence\playlist' playlist
.venv\Scripts\python.exe tests/validate_b3_lifecycle.py 'D:\YouTube视频下载\B3 evidence\lifecycle-retest'
$env:QT_SCALE_FACTOR='1.5'
.venv\Scripts\python.exe tests/validate_b3_layout.py 'D:\YouTube视频下载\B3 evidence\layout-150'
```

Network-dependent commands can fail if the source changes or YouTube requests
authentication. Do not replace failed evidence with later successes. The 4K
retest and standalone full 8K decode supplement the original batch; they do not
make its original exit status successful.

## Real desktop source runs

Normal source: `https://www.youtube.com/watch?v=E86EwGT_c2M`.
Its Preview returned 53 formats and 38 B2 quality profiles. The UI showed 4320P,
Best selected 571+251, and the created task retained that exact selection.

| Case | Preview / selection | Download / final validation | Result |
|---|---|---|---|
| 1080P | Bound native 1080P profile, 399+251 | 1920×1080 AV1 + Opus MP4, 47,913,467 bytes | PASS |
| 4K cancel/resume/retry | Bound native 2160P profile, 401+251 | Retest: 3840×2160 AV1 + Opus MP4, 324,633,310 bytes | PASS on retest; initial 403 retained |
| Best / 8K | Real 4320P UI and task selection, 571+251 | 7680×4320 AV1 + Opus MP4, full file and full decode | PASS |
| Audio Only MP3 | B2 best audio, 251; explicit MP3 extraction | MP3 audio stream, 2,590,628 bytes | PASS |
| Custom Format | Explicit advanced `bv[height<=720]+ba/b` | 1280×720 AV1 + Opus WebM, 28,819,170 bytes | PASS |
| Basic playlist | Title/count 1, Download All | aqz-KE-bpKQ: 3840×2160 AV1 + AAC, 60 FPS | PASS |

Playlist URL: `https://www.youtube.com/playlist?list=PLt5yu3-wZAlSLRHmI1qNm0wjyVNWw1pCU`.
The harness marks its retained task selection as absent (native callback mode);
this is not a Custom Format assertion. B2 selects each entry in the worker.
Large/multi-entry online playlist stress is not claimed.

### Full 8K acceptance

File: `D:\下载测试\YouTube视频\B3验证\8k_E86EwGT_c2M.mp4`.

| Field | Actual evidence |
|---|---|
| Native video / audio IDs | 571 / 251 |
| UI / task | 8K · 4320P · 30 FPS · AV1 · SDR; task FormatSelection exact match |
| Dimensions | 7680 × 4320 |
| Video | AV1, yuv420p, r_frame_rate and avg_frame_rate = 5991/200 |
| Audio | Opus, duration 154.781 seconds |
| Container / file duration | MP4, 154.781 seconds |
| File size | 614,003,516 bytes |
| SHA-256 | 6b69bb0265c2ede9b2ac86fff8576ae6ac35dc2e13934269ee06b88a966d1198 |
| Full decode | FFmpeg exit 0, error log 0 bytes |
| Upscale / video re-encode | None; native streams merged by existing chain |

Probe: `desktop\8k-ffprobe.json`. Decode:
`desktop\decode-result.json`, `decode-progress.log`, `decode-errors.log`.
The initial batch skipped its built-in decode because 4K had failed; the separate
decode ran against this exact downloaded file, with no section/duration limit:

```text
ffmpeg -v error -stats_period 10 -progress pipe:1 -i <8K file>
  -fps_mode passthrough -enc_time_base:v demux -f null -
```

### 8K60 / HDR / future resolution

Real HDR source: `https://www.youtube.com/watch?v=hVvEISFw9w0`.
Preview returned 70 formats and 54 quality profiles. B2/UI selected 702+140 with
4320P, 60 FPS, HDR10 and AV1. PASS means **metadata/UI/selection**; full HDR10 or
8K60 download/decode was not performed. Unknown-range rendering has a separate
test ensuring it is not mislabeled SDR/HDR.

8640P / 60 FPS / HDR10 was injected as a synthetic source format through the
actual B2/GUI boundary. It appears without truncation or a maximum-resolution
rule. This is synthetic UI PASS, not a claim of real >8K YouTube media.

## Authentication and proxy

| Browser / source | Profile | Preview | Download | Result | Notes |
|---|---|---|---|---|---|
| cookies.txt | Controlled local fixture | PASS | PASS | PASS | Server required Cookie; every recorded request authenticated |
| Firefox | Controlled parameter test | Parameter PASS | Parameter PASS | Native session NOT TESTED in B3 | Best Effort policy retained |
| Chrome | UI policy test | Policy PASS | Policy PASS | Native session NOT TESTED in B3 | Windows Experimental, cookies.txt fallback |
| Edge | UI policy test | Policy PASS | Policy PASS | Native session NOT TESTED in B3 | Windows Experimental, cookies.txt fallback |

The controlled cookie test also sets a test User-Agent through the common options
path. Preview and Download use the same cookie source/header/proxy context.
Changing authentication requires re-analysis. Existing B0.2 browser runtime
results and product gate are unchanged; this phase does not claim newly verified
personal YouTube browser login.

HTTP, SOCKS5 and SOCKS5H each carried real YouTube Preview and original Opus audio
download through an authenticated loopback proxy. Each recorded 7 requests,
correct credentials and zero residual children. Proxy values/passwords are
masked; log scans found no fixture secret or Cookie/SID/HSID/SAPISID value.
Evidence: `desktop\summary.json`, `desktop\logs\desktop.log`; no secrets copied
to reports/history/Git.

## Lifecycle, layout and limitations

`lifecycle-retest\lifecycle.json`: completed download + deliberately slow remux,
Cancelled task, confirmed active exit, all 5 pages visited while window moved;
maximum running-event-loop interval 0.0435941 seconds, child count 0. Real special
character/Chinese filename was sanitized by yt-dlp; none of `:?*"<>|` remained
as forbidden ASCII filename characters. 363/38/30 timer ticks occurred in the
complete/cancel/exit stages. Close-No and threaded Qt delivery also pass unit
integration checks.

Layout screenshots/JSON: `layout-100`, `layout-125`, `layout-150`.
Both 1366×768 and 1920×1080 physical-size targets passed all three Qt scale
factors; runtime devicePixelRatio was 1, 1.25 and 1.5. This uses Qt scaling on
Windows, not global OS display-setting changes. Download remained visible; all
pages were navigated. Settings Save is pinned. Lower settings/details scroll;
wide Queue details may require horizontal scrolling. Long titles wrap/truncate
in the card and retain full tooltips.

The original desktop batch maximum interval includes widget initialization and
synchronous ffprobe calls in the test harness, so its 0.936-second number is not
an app-only latency measurement. The separate lifecycle test isolates the
running UI loop. An additional online all-page stress attempt was blocked during
Analyze by YouTube's sign-in/bot-confirmation response; it did not download any
media and is not PASS. See `responsiveness\attempt.json` and
`D:\YouTube视频下载\B3-responsiveness.log`. Real full resolution downloads and
their evidence remain intact; specific all-page online stress for all three
resolutions is PARTIAL. No authentication bypass was attempted.
