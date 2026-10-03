# B5.0.1 original failure analysis

Branch: codex/b5-0-1-runtime-baseline. Starting base/tag: e9f7d023cf90970b55ebcdfa34f6f376f9f1af9e / v0.9.0-rc1.

The B5.1 UI draft was protected with git stash push -u before switching branches. Stash d25e88f3bfae0e4dfc06996c5ce160a2ab19021d protects 11 modified tracked files and 10 untracked files. File/blob inventory: evidence/b5_0_1/ui-draft-preservation.json. The worktree was clean after stashing. No UI changes belong to this fix.

Before changing any tests, the two failures were reproduced independently (evidence/b5_0_1/initial-failures.txt):

| Test | Expected | Actual |
|---|---|---|
| test_actual_health_with_utf8_build_configuration | 8.1.3-g330caae0c1-md-b43-r1 | 8.1.3-g330caae0c1-md-b43-r2 |
| test_native_runtime_and_sources_match_pins | avcodec-62.dll SHA256 c0ef153d97aae81b06f0506e6781c9e8b73cef07ef3a7d62714961f81334828b | ed2983fbeed3925b69181692c574dbe386f21ae403dac1ae57ec47f3d2f26937 |

Expected and actual binary location: D:/YouTube视频下载/yt-dlp-gui/dist/MediaDownloader/bin/.
Expected hashes came from build/runtime-lock.json at the stable tag. Actual hashes came from those exact files, not filenames or PATH fallback. Both tests do not load GUI code.

Root cause: b9794ef0f01f5a1361aec5576abca3cb72015300 rebuilt/repackaged native FFmpeg as r2 to support chapter metadata. Later checkout to the older B5 source did not rewind ignored dist, bin and .tools products. Consequently old source/pins/tests were combined with newer r2 binaries. This is a local artifact/source-baseline mismatch.

Fix: adopt the proven complete r2 runtime, align recipe/lock/notices and release-test manifest/checksums, retain exact version/hash checks, strengthen FFmpeg/FFprobe equality and receipt/config checks. Add the existing real yt-dlp chapter regression from the repair commit. No format selection, download algorithm, QuickJS strategy or queue/history behavior changed.

Two former failures: 2 PASS (evidence/b5_0_1/two-tests.txt).
Full baseline suite: 167 previous PASS + 1 new PASS = 168 PASS (evidence/b5_0_1/full-tests.txt).
