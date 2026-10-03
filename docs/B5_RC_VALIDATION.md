# B5 Release Candidate Validation

**B5 = PASS; Internal RC = READY.** Technical Release Gate=PASS;
Clean Machine Gate=NOT TESTED; Public Distribution Gate=NEEDS LEGAL REVIEW.
These are separate conclusions.

## Git and build identity

Started on clean `codex/b4-4-clean-machine-acceptance` at
`bf9eb8537d5f15b8da48c9f9044121849c41dfc2`; created `codex/b5-product-polish`.
Final runtime/build source commit: `db9b7411c8882f39d1e56b295c35a01f2e3dd2c5`.
The completion commit adds validation documents, test tooling/evidence and test-kit metadata;
it does not change compiled product code. The manifest identifies the actual committed build inputs.
Historical B0–B4 outcomes and master/earlier branches are unchanged. No public release/tag is created.

Environment: development host Windows 11 Pro 10.0.26200, AMD64, Python 3.13.13 installed.
Frozen targets run with a Windows-only child-process PATH and isolated test profiles.
This is local runtime isolation, **not** an independent Windows environment.
Windows window control failed to initialize because the kernel assets path was unavailable.
Acceptance uses the existing `--validate-release` entry, real Qt windows/buttons and Manager.
Screenshots use QWidget.grab; they are actual application renders.

## Exact final artifacts

| Artifact | Bytes | SHA256 |
|---|---:|---|
| MediaDownloader-Portable.zip | 251425379 | 7e040de3b813de60cad24a3084a0a2659c214d23c97a90fb5beee537036acca1 |
| MediaDownloader-Setup.exe | 239462959 | af396b6b45aa0cb36d70998e6665c6ac20a36c7203f1d8ea4ef2d2584f604de2 |

Build command: `.venv\Scripts\python.exe build_windows.py`.
Both artifacts, checksums, release manifest and Release Notes are identically copied to `release-test`.
Media Downloader / 0.9.0-rc1 appears in UI/About/logs/diagnostics, application EXE and installer ProductVersion.
Windows binary numeric fields derive **0.9.0.1** from the single version source. Inno FileVersion is numeric,
not a second release version. [Inno numeric product field](https://jrsoftware.org/ishelp/topic_setup_versioninfoproductversion.htm)
and [text product field](https://jrsoftware.org/ishelp/topic_setup_versioninfoproducttextversion.htm) describe this distinction.
Both executables use the Windows GUI subsystem and contain icon resources. Four existing icon sizes have
identical pixels; Qt can write different PNG physical-DPI metadata before/after QApplication initialization.

## Real frozen application regression

| Package | Case | Actual result | Formats | Selected height | FPS metadata | Range |
|---|---|---|---:|---:|---:|---|
| Portable | 1080P complete | completed | 53 | 1080 | 30 | SDR |
| Portable | 4K | metadata-pass | 53 | 2160 | 30 | SDR |
| Portable | Best Quality / 8K | metadata-pass | 53 | 4320 | 30 | SDR |
| Portable | 8K60 HDR10 | metadata-pass | 70 | 4320 | 60 | HDR10 |
| Portable | MP3 Audio Only | completed | 53 | -- | -- | -- |
| Portable | cookies.txt fixture | completed | 1 | -- | -- | -- |
| Portable | HTTP proxy audio | completed | 53 | -- | -- | -- |
| Portable | SOCKS5 proxy audio | completed | 53 | -- | -- | -- |
| Portable | SOCKS5H proxy audio | completed | 53 | -- | -- | -- |
| Portable | Cancel → Retry | completed after cancellation | 53 | 1080 | 30 | SDR |
| Installed | 1080P complete | completed | 53 | 1080 | 30 | SDR |
| Installed | 4K | metadata-pass | 53 | 2160 | 30 | SDR |
| Installed | Best Quality / 8K | metadata-pass | 53 | 4320 | 30 | SDR |
| Installed | 8K60 HDR10 | metadata-pass | 70 | 4320 | 60 | HDR10 |
| Installed | MP3 Audio Only | completed | 53 | -- | -- | -- |

Sources: [E86EwGT_c2M](https://www.youtube.com/watch?v=E86EwGT_c2M) (8K30 SDR)
and [hVvEISFw9w0](https://www.youtube.com/watch?v=hVvEISFw9w0) (8K60 HDR10).
Both packages displayed true 4320P and selected it for Best Quality. Core profile objects/format expressions
remain equal through English/Chinese switches; screenshots verify navigation/page identity and visible Download controls.
1080P final files in both packages: **1920×1080, AV1 video + Opus audio, MP4, yuv420p,
5991/200 FPS, 154.732098-second video stream**. Full bundled-FFmpeg decode returned 0 with no error output.
Metadata rounds FPS to 30; ffprobe's rational rate is retained rather than reported as exactly 30.
MP3 Audio Only completed with an audio stream. Cancel used the existing Retry action, creating a new completed task.
The cancelled task remains in history. [Portable results](evidence/b5/portable/results.json),
[Installed results](evidence/b5/installed/results.json), [Portable ffprobe](evidence/b5/portable/portable-1080-ffprobe.json).

Cookies.txt used a controlled Cookie-required HTTP fixture with the same Preview/Download authentication.
All requests met its Cookie requirement. This is not a new claim of a logged-in YouTube browser test.
HTTP/SOCKS5/SOCKS5H proxies forwarded real YouTube audio downloads and authenticated at controlled proxies.
Only boolean metrics are retained; Cookie files and raw test specs containing proxy secrets are excluded.
Credential-sentinel scanning of both final logs passed.

Runtime Health is READY. All eight native FFmpeg files and QuickJS match B4.3 lock hashes.
Portable/Installed native paths: `bin/ffmpeg.exe`, `bin/ffprobe.exe`, `bin/runtime/qjs.exe` under each actual root.
yt-dlp 2026.8.19 is the frozen Python package; FFmpeg/FFprobe=8.1.3-g330caae0c1-md-b43-r1;
QuickJS-NG=0.17.0; independent EJS=0.8.0.
[Portable paths](evidence/b5/portable/summary.json) and [Installed paths](evidence/b5/installed/summary.json)
retain complete locations. No worker children or B5 application/native-tool processes remained after normal exits.

## Product experience

Both languages cover the five pages, seven Settings groups, Welcome, About, Help, errors,
status bar, headers/actions and Runtime Health. Missing translation keys=0.
First-launch language/folder save uses the actual Welcome action. A second real Qt process loaded saved Chinese,
the Chinese/space folder, and **8 Portable / 2 Installed history records**.
No account workflow is added. Audio Only disables video selection/container controls.
Log copy redacts secrets; Clear View retains the file. Cancelling Clear History preserves records.
About opens local notices. Codec hints consume Core families and never change the selected format.

100%/125%/150% Qt scaling, Light/Dark/System, both languages and a long synthetic >8K title passed.
For the 1366×768 physical target, logical client sizes were 1346×708 / 1072×554 / 890×452.
Minimum window is 720×440; Download remains pinned/visible and Settings scrolls.
This verifies Qt scaling without claiming a Windows display-settings change or accessibility certification.
Screenshots: [Chinese 8K60 HDR](evidence/b5/portable/8k60-hdr-ui/zh-download.png),
[English About](evidence/b5/portable/product-startup/en-about.png),
[150% Chinese Cookies](evidence/b5/layout-150/dark/zh-settings-cookies.png).

Inno compilation and actual current-user Chinese installation succeeded without elevation.
Desktop/Start Menu shortcuts target the correct application; it launched normally, downloaded 1080P
and persisted Settings/history through restart. [User context](evidence/b5/installer-user-context.json).
No independent Windows uninstall/delete/crash acceptance is claimed; B4.4 remains pending.

## Tests and file-level review

**Previous=151 PASS; New=16 PASS; Total=167 PASS; 0 failures, errors or skips; 51.800 seconds.**
[Full unit output](evidence/b5/unit-tests.txt).
All old tests remain present. Legacy browser/text assertions now use stable raw values or the new UI wording.
New cases cover version/About identity, catalog parity/placeholders, missing-key fallback, live bindings/status bar,
raw option equality, merge progress, codec hints, error/redaction categories, runtime labels, browser labels,
Welcome persistence, RC/help, history confirmation/log copy, license entry, packaged materials and manifest hashes.

Additional scripts: `tests/validate_b5_layout.py`, `tests/validate_b5_frozen.py`, `tests/validate_b5_artifacts.py`.
The last reuses the existing actual payload comparison. **1341 payload files** match byte-for-byte
in staging, the actual ZIP and installed payload; 1350 embedded modules. All 13 pinned source/notice inputs verified.
Only qtbase_zh_CN.qm is added; excluded Qt plugins/translations, Deno and PyInstaller analysis modules stay excluded.
README, notices, license texts and source/relink materials are present in both final packages, with original attribution.
[Payload validation](evidence/b5/artifact-validation.json), [PE/version/icon facts](evidence/b5/product-metadata.json).

Active product UI/entry/artifact branding is Media Downloader. Original names remain in attribution,
historical/source documents and legitimate filesystem paths.
`git diff <B4.4-base> -- core models services` is empty. Selection/order/options/merge/cancel/retry architecture
and native runtime bytes are unchanged. B5 ran complete 1080P and 4K/8K metadata checks;
previous full 4K/8K evidence in B4.3 remains valid and is not relabeled as a new B5 download.

P0=0; P1 Technical=0; P1 Distribution=2; inherited P2=2; language-coverage P3 is closed (P3=0).
