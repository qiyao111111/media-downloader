# B5.1 regression — PASS (local technical scope)

Baseline reconciliation B5.0.1 is complete. The restored UI draft was retained on `codex/b5-1-ui-polish`; baseline commit is `dbd429367bc82db4d33fb4219a9496c23740b86d`. FFmpeg/FFprobe remain `8.1.3-g330caae0c1-md-b43-r2`; QuickJS 0.17.0 and yt-dlp 2026.8.19. The protected RC1 tag remains unchanged.

## Tests

- Previous tests: 168 PASS / 0 FAIL before new tests (`evidence/b5_1/previous-168-tests.txt`).
- New Qt tests: 28 PASS / 0 FAIL, including final display fixes (`new-28-tests.txt`).
- UI full suite: 196 PASS / 0 FAIL (`ui-full-196-tests.txt`).
- Final RC2 full suite: 196 PASS / 0 FAIL, 285.117s (`rc2/full-196-tests.txt`), after the version/build and all final display fixes.
- The original stopped-run logs `tests.txt` and `baseline-runtime.txt` are historical evidence of the subsequently resolved r1/r2 mismatch, not current results.

## Real GUI and download regression

`tests/validate_b5_1_live.py` uses the existing release-validation runner, actual MainWindow, Qt buttons and Manager. Profiles/output directories are isolated under temp; validation does not touch user credentials or personal history. Evidence is in `evidence/b5_1/live`.

| Case | Result | Evidence |
|---|---|---|
| Launch/runtime | PASS | actual source Qt window, all bundled runtime health Ready, zero child processes at exit |
| 1080P | PASS | 399+251; completed 47,913,472-byte MP4; 1920x1080 AV1 plus Opus; full decode exit 0/no errors |
| 4K UI | PASS | selected 401+251, 2160P, actual quality options |
| 8K UI | PASS | Best = 571+251, 4320P, actual 8K/4320P chips |
| 8K60 HDR UI | PASS | real source hVvEISFw9w0, 702+140, 4320P/60 FPS/AV1/HDR10; metadata/UI only |
| Audio | PASS | actual MP3 output 2,590,629 bytes; full decode exit 0/no errors |
| Cancel / Retry | PASS | actual Cancel button after >1MiB; cancelled task; actual Retry button; new task completed; resumed first progress 2,097,152 bytes |
| Open Folder | PASS | completed row button clicked on actual output |
| Queue/History | PASS | real state captures and persisted completed/cancelled records |
| Settings/Logs | PASS | actual health, categories retain option values, secret masking/redaction, log/empty transitions |
| Theme/language restart | PASS | separate save/restart processes, Dark and English retained; Missing Keys = 0 |
| Errors | PASS presentation | invalid input extracted live; network/403 injected typed errors, inline reason and Retry, safe details dialog |

Final downloading/merging/completed captures after the last table fixes use a further real 1080P run in `evidence/b5_1/final-capture`. Completed size now shows the final file, not the last audio-stream progress size. All original selection/controller/storage/runtime files outside presentation remain unchanged.

1080P, audio and retry outputs have complete FFmpeg decode evidence in `live/decode-summary.json`. Full 8K60 HDR download/color fidelity is not claimed. This stage validates its metadata and UI only.

## Release status

UI commit: `6b41f84595d9da00cc746eacb4b41f891e706496` (`feat: refine desktop UI and visual design system`), followed by a verified clean worktree. RC2 source/build commit: `af9949a35e53b1b27d4416010e639ac9187dd596`. The Single Source of Truth is `app/version.py`: 0.9.0-rc2 / Windows tuple (0,9,0,2). The exact version assertions were updated accordingly. The existing B4 pipeline now selects release notes by VERSION.

`build_windows.py` exited 0. Portable ZIP = 251,499,102 bytes; Installer = 239,503,842 bytes. Both release-test copies match SHA256 and the manifest. The manifest includes Product, Version, committed build revision, timestamp, r2/yt-dlp/QuickJS versions and both artifact hashes. The shared QSS, notices, licenses and source/relink materials are in the Portable archive; validation profiles are absent. EXE and Setup ProductVersion both read 0.9.0-rc2. The full build log and artifact verification are in `evidence/b5_1/rc2`.

Local frozen Portable and installed-mode payload each passed five cases: actual 1080P completion, 4K/8K/8K60 HDR10 metadata and MP3 completion. Both video/audio outputs fully decoded with zero errors, runtime paths stayed in the corresponding bundle, selection remained unchanged across English/Chinese captures, Missing Keys = 0, and child processes = 0 on exit. Both modes used a PATH limited to Windows directories and isolated configuration. Setup was compiled and its version/hash verified; it was not freshly installed in this run. Installed-mode checks run the exact onedir payload that Setup packages, not a clean-PC installation.

The legacy frozen screenshot helper still iterates former collapsible Settings sections, so those Settings images are excluded from B5.1 visual evidence. Final Settings acceptance comes from the updated category-aware source matrix. RC2 About and HDR screenshots are recorded separately in `screenshots/b5_1/rc2`.

No RC2 tag was created. RC1 still resolves to its original commit. The final evidence commit can differ from build_commit because it only records QA helpers, reports and generated release-kit metadata; application/build source remains the compiled revision.

Technical Release Gate: PASS (local UI, runtime, build and frozen-payload scope).
Clean Machine Gate: NOT TESTED. Public Distribution Gate: NEEDS LEGAL REVIEW.

P0=0; P1 Technical=0; P1 Distribution=2 (independent clean Windows acceptance and professional distribution review). Inherited P2=2 (upstream/authentication limitations and older-player codec support); P3=0. Native Windows display-setting/DWM checks remain outside the local Qt scaling scope.
