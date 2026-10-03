# B2 Regression

Date: 2026-10-02. Base 744de1ecc0ecfa233f36a189f91959b2dd43f46e, clean worktree, new codex/b2-format-selector branch. No changes to master/B1, dependencies, engine architecture or B3 scope.

## Tests and runtime evidence

`python -m unittest discover -s tests -v`: **61 PASS** (16 existing + 45 new). Final output: `D:\YouTube视频下载\B2-tests-final.log`.

| Check | Result | Evidence |
|---|---|---|
| Application launch/interactive Qt | PASS | gui/gui-results.json; window/settings movement, 0.0286 s maximum event-loop gap |
| Preview | PASS | Native metadata through same builder/callback as download; all desktop case previews succeeded |
| 1080P complete download | PASS | desktop-final/1080p-ffprobe.json: 1920x1080 AV1 + Opus, 154.781 s |
| 4K complete download | PASS | desktop-final/4k-cancel-retry-ffprobe.json: 3840x2160 AV1 + Opus, 154.781 s |
| 8K complete download + decode | PASS | formats-final/results.json and ffprobe.json |
| Audio Only | PASS after retry | audio-retest/desktop-results.json: full MP3 with audio stream |
| Resume | PASS | 4K retry first transfer reports 34,592,727 bytes, then completes |
| Cancel/Retry | PASS | Real 4K cancellation and table Retry; GUI cancel-all and worker shutdown |
| cookies.txt | PASS | Cookie-gated local media; Preview and Download use controlled file, no personal browser cookies |
| HTTP / SOCKS5 / SOCKS5H | PASS | Three authenticated loopback forwarders, real public YouTube audio completed |
| Queue | PASS | Existing duplicate/transition/retry tests plus real desktop task submissions |
| History | PASS | 8 recorded desktop tasks with correct terminal status; legacy/serialization tests |
| Settings | PASS | Existing settings/preset tests; new quality-target/preset/custom routing test |
| Logs | PASS | Redaction/rotation tests, source metadata excluded from profile repr, final source reasons contain no headers |
| Custom Format | PASS | Native ba full download plus raw-expression preservation tests; existing custom b cookie fixture |
| Muxed fallback | PASS (offline native-model contract) | Valid muxed retained when split pair unavailable; no invented audio stream |

All paths above are relative to `D:\YouTube视频下载\B2 evidence\` unless absolute. `desktop-final/desktop-summary.json`: 8 cases, 8 history records, no worker children; maximum tick gap 0.8112 s (includes synchronous test ffprobe while another validation decodes 8K). Dedicated GUI smoke remains below 0.03 s.

## Failures retained, not rewritten

The final desktop batch completed 7/8 cases and exited 1 because Audio Only received YouTube HTTP 403 before any bytes. The app entered failed and retained the diagnostic, with zero worker children. The same source, dynamic audio selector and MP3 settings were rerun separately in `audio-retest` and completed successfully (exit 0). This is reported as PASS after retry, not a clean first-attempt pass. No code change or fallback to a different quality was used for that retry.

An earlier development run (`desktop`, `formats`) used a policy that preferred slightly higher-bitrate DRC audio. Its raw results are preserved, but they are not evidence for the final audio policy. `desktop-final`, `formats-final` and `audio-retest` are the authoritative final-policy runs. The separate public BaW_jenozKc test source was unavailable and is not counted as a successful test.

## Commands

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tests/validate_b1_desktop.py 'D:\YouTube视频下载\B2 evidence\desktop-final' --dynamic
.venv\Scripts\python.exe tests/validate_b1_desktop.py 'D:\YouTube视频下载\B2 evidence\audio-retest' --dynamic --only audio
.venv\Scripts\python.exe tests/validate_gui.py 'D:\YouTube视频下载\B2 evidence\gui'
.venv\Scripts\python.exe tests/validate_b2_formats.py 'D:\YouTube视频下载\B2 evidence\formats-final'
```

## Severity and stage gate

Final B2 result: **PASS**. B3 integration may proceed as a separate stage; B2 stops here.

- P0 Critical: 0.
- P1 High / blocking B3: 0. Native 8K final file and full decode passed.
- P2 Medium: three open groups below, none requires B3 UI work in this stage.
- P3 Low: one inherited version-label inconsistency (package 3.0.0 versus About 3.1).

Still open:
1. P2: upstream extraction/network variability. No supported JS runtime is enabled in the existing baseline; yt-dlp warns some server formats may be absent, and one transient HTTP 403 occurred. B2 selects the best valid formats actually returned, never claims access to every server/client representation. Runtime/EJS hardening remains follow-up; B3 UI integration is not blocked by the demonstrated successful downloads.
2. P2: Windows Chromium cookies remain experimental due to locks/DPAPI/App-Bound Encryption. B0.2 policy remains: cookies.txt supported, Firefox best effort. Not retested against personal browser data in B2; no B3 blocker.
3. P2: FFmpeg/container and player compatibility varies; MP4 AV1+Opus is verified on FFmpeg 8.0, while MKV/Opus probing previously emitted a diagnostic. Older toolchains and every player are not certified. See container policy; no silent transcode fallback and no B3 blocker.

8K60/HDR is metadata/selection validation only, not a claim of a full HDR download. Synthetic 8640P proves no software ceiling, not that a real 16K file was downloaded. Existing JSON atomicity/advanced-feature deferrals remain outside B2. No installer, updater, platform addition, brand work or B3 development performed.
