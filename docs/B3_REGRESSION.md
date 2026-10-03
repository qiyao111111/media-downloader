# B3 Regression

B3 integration gate: **PASS**. Existing = **61 PASS**, New = **44 PASS**,
Total = **105 PASS**, final unittest run 7.065 seconds.
Command: `.venv\Scripts\python.exe -m unittest discover -s tests -v`.
Evidence: `D:\YouTube视频下载\B3-final-tests.log`.

The 44 new tests cover every requested UI integration case and additional stale
preview, auth/netrc invalidation, exact task selection, no fake quality, unknown
range, explicit container override without automatic recode, postprocessing,
indeterminate total, playlist/batch, long title, experimental browser policy,
profile handoff, custom format, close decline, ownership/page navigation, active
history retention, worker Qt signals, safe folder opening and empty Queue state.
No new GUI testing framework was installed.

## Verification matrix

| Item | Status | Evidence / boundary |
|---|---|---|
| Application Launch | PASS | Actual MainWindow in online/local/layout harnesses |
| Analyze | PASS | Async real sources; controlled success/failure/stale/repeat tests |
| Metadata | PASS | Real titles/channel/duration/highest; missing fields tested |
| Thumbnail | PASS | Async Qt Network with timeout/placeholder; not required for extraction success |
| 1080P UI | PASS | Native profile binding and final 1920×1080 AV1 + Opus |
| 4K UI | PASS | 3840×2160 completed isolated retest; initial 403 preserved |
| 8K UI | PASS | Real 4320P dropdown, Best binding, exact task selection, full file/decode |
| 8K60 UI | PASS | Real 4320P60 metadata/selection; full download not claimed |
| HDR UI | PASS | Real HDR10 metadata/selection; UNKNOWN stays UNKNOWN |
| >8K Synthetic UI | PASS | 8640P injected through B2; no actual >8K download claim |
| Best Quality | PASS | Manager/B2 source only, exact FormatSelection handoff |
| Audio Only | PASS | Real MP3 extraction and original Opus outputs via proxy cases |
| Custom Format | PASS | Explicit advanced 720P expression, completed real download |
| Container Auto | PASS | B2 policy unchanged, real MP4 and original audio containers |
| Container override | PASS | Explicit notice; MKV stream-copy lifecycle, no automatic recode |
| Download | PASS | Full 1080P, 4K, 8K, audio, custom and playlist files |
| Progress | PASS | Real record events and determinate/indeterminate tests |
| Speed | PASS | Record-based KB/MB/GB per second; unit assertion 2 MB/s |
| ETA | PASS | Record-based MM:SS/HH:MM:SS, unknown -- |
| Postprocessing | PASS | Actual FFmpeg stage, Merging label and lifecycle slow remux |
| Cancel | PASS | Real task cancellation, Cancelled terminal state |
| Retry | PASS | New worker, duplicate guard, real cancelled 4K task resumed |
| Resume | PASS | Retried 4K first positive byte record 124,102,438; final file validated |
| Queue | PASS | Current-session records/actions, terminal retry, empty/duplicate guards |
| History | PASS | Terminal-only rendering/persistence/actions; active records preserved |
| Settings | PASS | Save/load tests, distinct concurrency fields, grouped real page |
| Logs | PASS | Actual desktop event/error log, redacted handler, Clear/Copy/Open Folder |
| Cookies.txt | PASS | Authenticated controlled real Preview/Download; B0.2 policy retained |
| Firefox Cookies | NOT TESTED | B3 native logged-in session not rerun; profile handoff/UI policy PASS, Best Effort |
| Chrome Experimental | NOT TESTED | B3 native session not rerun; Experimental/fallback UI PASS |
| Edge Experimental | NOT TESTED | B3 native session not rerun; Experimental/fallback UI PASS |
| Credential logging | PASS | Existing redaction tests, mapper tests, live fixture log scan |
| Error mapping | PASS | Typed redacted details, no UI traceback; live initial 403 diagnosed |
| HTTP Proxy | PASS | Real Preview/Opus download, 7 authenticated requests |
| SOCKS5 | PASS | Real Preview/Opus download, 7 authenticated requests |
| SOCKS5H | PASS | Real Preview/Opus download, 7 authenticated requests |
| Chinese Path | PASS | Actual UI Save To under D:\下载测试\YouTube视频\B3验证 |
| Long Title | PASS | Synthetic long Chinese/special title, plain text/wrap/tooltip, layout checks |
| Special Characters | PASS | Real download filename sanitized by yt-dlp |
| Playlist | PASS | Real one-entry title/count/Download All; controlled multi-entry presentation |
| Multiline URL | PASS | Duplicate removal and independent task options integration test |
| App Exit | PASS | Decline test; live confirmed active exit, zero child processes |
| Main-thread delivery | PASS | Worker Qt signal test, real all-page lifecycle without crashes |
| 1366×768 / 1920×1080 | PASS | Six real Qt physical-size/scaling layout cases |
| DPI 100/125/150 | PASS | Qt runtime factors verified; global OS settings not changed |
| High-resolution online page-switch stress | PARTIAL | Full online downloads/moving window passed; extra all-page attempt blocked at Preview; dedicated all-page local lifecycle PASS |
| Full app translation | PARTIAL | Navigation en/zh; existing mixed-language detailed controls |
| JavaScript Runtime | NOT IMPLEMENTED | Explicitly Deferred under B3 scope |
| Atomic JSON persistence | NOT IMPLEMENTED | Existing writer unchanged, Deferred |

## Evidence integrity and severity

The first online batch has 9 successful cases and one 4K HTTP 403 failure. Its
exit 1 and original JSON/log remain unchanged. The isolated 4K retest completed;
standalone 8K full decode returned 0 with no errors. The initial layout native
crash was fixed at Qt widget ownership and now has a regression test; it is not
an unresolved P1. Lifecycle's initial startup timing assertion was corrected and
the original measurement retained. The optional online stress attempt later
hit a source authentication challenge; it is never represented as successful.

Unresolved: P0 **0**, P1 **0**, P2 **3**, P3 **1**.

1. **P2 — source availability / JS runtime Deferred:** YouTube can return 403 or
   login/bot confirmation. Preserve diagnostics and supported cookies.txt path;
   runtime distribution/JS work is outside B3.
2. **P2 — non-atomic JSON:** existing settings/history can lose persisted data
   during an interrupted write; minimal atomic-save work remains later scope.
3. **P2 — player/container compatibility:** source AV1/VP9/Opus may need a capable
   player; no silent video transcoding is introduced.
4. **P3 — partial translation:** main navigation only is translated by the
   language toggle, as labeled in Settings.

Native browser convenience remains governed by B0.2: cookies.txt Supported,
Firefox Best Effort, Windows Chrome/Edge Experimental. Not rerunning those native
sessions does not revoke the existing product authentication gate.

`master`, `codex/b1-architecture-cleanup` and `codex/b2-format-selector` are
unchanged. No B4 packaging or other stage work was performed.
