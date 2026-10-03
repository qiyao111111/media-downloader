# B3 UI Integration

Base: B2 `ec9c2950ecdb487455dd090470835ce95650e51e`.
Branch: `codex/b3-ui-integration`. Start workspace was clean. Protected master,
B1 and B2 branch references remain unchanged.

## Result

B3: **PASS** for the defined desktop integration gate. P0 = 0, unresolved P1 = 0.
Existing 61 tests and 44 new Qt integration tests pass (105 total).
Online source availability remains a P2 limitation, with failed attempts retained
alongside successful acceptance runs. This report does not claim every YouTube
request succeeds or native Chrome/Edge extraction is supported.

## Changes

| Area | Integration |
|---|---|
| Main navigation | Five pages, scrollable content, pinned Download and Save actions |
| Preview | Manager executor, typed errors, generation guard, async thumbnail |
| Quality | B2 profiles bound as item data; Best/audio/explicit profile selection through Manager |
| Download | FormatSelection retained by DownloadTask; native options built in Core |
| Batch/playlist | Independent B2 selection per video, lightweight playlist preview |
| Queue | Canonical record snapshots, readable metrics, cancel/retry/remove/open-folder |
| History | Terminal records only, safe native file actions, active history preservation |
| Settings | Existing controls/services, explicit groups/Save, profile and retry fields, masked proxy |
| Logs/errors | Common redacted mapper, bounded log view, local clear/copy/folder actions |
| Tools/exit | Async Core tool inspection, confirmed active-exit cancellation/cleanup |

Minimal Core adjustments are selection/title handoff, retry snapshots, Manager
preview/selection/tool inspection entry points, dynamic range in safe runtime
metadata, and preservation of typed format/auth errors over IPC. The option
builder only adds stripping of UI-only browser_profile. It does not change B2
ranking, expression construction, FFmpeg commands, resume or process isolation.

## Bugs found and resolved

| Finding | Root cause / fix | Evidence |
|---|---|---|
| Qt TypeError on selection change | Bool/index payload sent to a zero-argument signal; connect through an argument-discarding lambda | New UI tests and live controls |
| Settings page native stack overflow | Two QScrollAreas retained the same widget after page transfer; explicitly takeWidget before reparenting | Ownership test, all-page live navigation and 6 layout cases |
| Raw progress coupling | Old Main consumed native hook data; use Manager record signals only | Worker-signal test and live Queue records |
| Stale preview/auth | Old selection could survive changed credentials/URL; generation checks and invalidation for cookie/profile/proxy/login/netrc | New stale/auth/netrc tests |
| Active history cleared | Clear action removed running records; reuse existing terminal-only clear_completed | New preservation test |
| Empty Queue Cancel All | Initially enabled without tasks; initialize disabled | New button-state test |

The first lifecycle assertion counted widget construction before the event loop
as a 399 ms interval. The harness now starts timing at exec(); retest recorded
44 ms maximum while switching pages, moving the window and running real
download/postprocessing/cancel/exit. This was a measurement correction, not a
runtime workaround. The original result is retained.

The first online batch completed 9 of 10 cases; a 4K Retry hit HTTP 403.
An isolated Analyze/cancel/Retry retest completed 4K and resumed from retained
bytes. A later optional online page-switch stress attempt met a YouTube sign-in/
bot-confirmation response during Preview and did not start a download. It is
recorded as BLOCKED, not PASS; no security workaround was attempted.

## Remaining issues

| Severity | Issue | Impact / handling |
|---|---|---|
| P2 | JS runtime Deferred; external 403/sign-in challenges | Anonymous source availability can vary. Keep diagnostics; use supported cookies.txt when appropriate. JS work belongs to a later authorized stage. |
| P2 | Existing JSON settings/history writer is not atomic | Interrupted writes can lose saved preferences/history. Underlying persistence implementation was not changed; atomic save remains Deferred. |
| P2 | AV1/VP9/Opus/container playback compatibility | Older players may reject an intact source stream. Recommend Auto/MKV; no silent video transcode. |
| P3 | Partial language coverage | English controls plus existing Chinese guidance; language toggle translates main navigation only and is labeled accordingly. |

Firefox remains Best Effort; Chrome/Edge on Windows remain Experimental under
B0.2 product policy. B3 tests the UI policy/parameter handoff, not a new native
browser login session. These convenience paths do not block the cookies.txt gate.
8K60/HDR proof is real metadata/UI/selection only; >8K proof is synthetic.

No packaging, installer, new platform, branding redesign or JS-runtime feature
was started. B3 stops after its commit.
