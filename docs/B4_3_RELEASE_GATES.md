# B4.3 release gates

2026-10-02 · codex/b4-3-release-simplification · base
b8b18a9acb8fa1ba01f6a51e17bb98b600a6ac0b · unsigned internal RC0.9.0rc1.

**B4.3 Result: CONDITIONAL PASS**

| Gate | Result | Scope |
|---|---|---|
| Technical Release Gate | PASS | final native/frozen functionality, build, packaging and regression below |
| Clean Machine Gate | NOT TESTED | no independent Sandbox/VM/PC; no PATH-isolation substitution |
| Public Distribution Gate | NEEDS LEGAL REVIEW | professional Qt/PySide/Microsoft final-term review; Inno business review separate |

P0=0; P1 Technical=0; P1 Distribution=2 (clean acceptance + professional
public-distribution review); inherited P2=2, P3=1. This is not authorization
to publish v1.0 or start B5. B4.2 history remains unchanged.

## Actual final native regression

All cases use the final own FFmpeg DLL/EXE hashes from runtime-lock.json and
QuickJS hash c6f2427ca3f9f1b45cd616ab92f6c49036957590a793afc1fa7526bd441bcddb.
The final RC native receipt/file hashes were rechecked after the diagnostics-only
Python rebuild: identical to the tested shipping native binaries.
Every media case downloads whole streams, checks duration/audio with ffprobe,
and decodes the complete output with final FFmpeg. No fragment/portion limit,
upscale, silent video recode, FPS reduction or HDR-to-SDR operation.

| Case | Result | Bytes | Duration seconds | Full-decode errors | Elapsed seconds |
|---|---|---:|---:|---:|---:|
| 1080p | PASS | 47913472 | 154.774000 | 0 | 25.112 |
| 4k | PASS | 324633315 | 154.774000 | 0 | 110.336 |
| 8k | PASS | 614003521 | 154.774000 | 0 | 256.21 |
| vp9-webm | PASS | 405228246 | 154.781000 | 0 | 153.252 |
| h264-mp4 | PASS | 86148483 | 154.807438 | 0 | 36.608 |
| av1-opus-mkv | PASS | 47875965 | 154.781000 | 0 | 34.117 |
| audio-mp3 | PASS | 2590629 | 154.761000 | 0 | 9.933 |
| audio-m4a | PASS | 6870017 | 154.761000 | 0 | 10.918 |
| audio-opus | PASS | 2489026 | 154.780500 | 0 | 9.077 |
| audio-flac | PASS | 27017760 | 154.761000 | 0 | 8.797 |
| audio-wav | PASS | 29714190 | 154.761000 | 0 | 8.733 |
| audio-best | PASS | 2489026 | 154.780500 | 0 | 8.732 |

Real 8K: E86EwGT_c2M, format571 video-only +251 Opus audio, 7680×4320 AV1
30 FPS, final614003521 bytes,154.774 s, video+audio, merge, ffprobe and complete
decode all PASS. H264137+140, VP9 313+251 WebM and AV1+Opus399+251 MKV also PASS.
Six existing audio formats MP3/M4A/Opus/FLAC/WAV/best PASS.
[Whole-stream results](evidence/b4_3/shipping-media-results.json),
[8K ffprobe](evidence/b4_3/shipping-media-8k-ffprobe.json),
[8K complete decode progress](evidence/b4_3/shipping-media-8k-decode-progress.log),
[8K decoder errors](evidence/b4_3/shipping-media-8k-decode-errors.log).

Separate real native challenge A/B and equal complete format-list comparison,
including 8K60 HDR10 source hVvEISFw9w0 (702+140), are in
[JS A/B report](B4_3_JS_RUNTIME_COMPARISON.md). No challenge/selector patches.
Actual native encoder and yt-dlp thumbnail postprocessor checks cover existing
OpenH264/VP9 encoding and PNG→JPEG→WebP→PNG, beyond capability-name inspection.

## Final frozen Portable and installed EXE

Two final actual RC payloads, each11 real Qt/MainWindow/Manager cases, exit0.
Fresh Chinese/space destinations prevent old-file cache/skip downloads being
counted as new full download evidence. Native paths remain within each release
root; embedded yt-dlp resides in its EXE PYZ/data, not host Python/yt-dlp.
Windows-only child PATH proves local frozen routing, not clean-machine PASS.

| Functional case | Portable | Installed |
|---|---|---|
| Actual visible app / Runtime Health | PASS | PASS |
| Anonymous preview + 1080P complete | PASS | PASS |
| 4K | complete + cancel/retry PASS | metadata/selection PASS |
| 8K / Best=4320P | complete PASS | metadata/selection PASS |
| 8K60 / HDR10 | metadata/selection PASS | metadata/selection PASS |
| Audio Only MP3 | PASS | PASS |
| cookies.txt gated preview/download + headers | PASS | PASS |
| HTTP / SOCKS5 / SOCKS5H authenticated proxy | PASS | PASS |
| Cancel / active-download normal exit | PASS | PASS |
| Saved settings + restart | PASS | PASS |
| History JSON + persistence | PASS;11 records equal | PASS; lifecycle/crash below |
| Chinese/space output paths | PASS | PASS |
| Zero child processes after normal close | PASS | PASS |
| Independent Clean Windows / Portable Delete | NOT TESTED | NOT TESTED |

Actual versions: yt-dlp2026.8.19, FFmpeg/FFprobe8.1.3-g330caae0c1-md-b43-r1,
QuickJS-NG0.17.0. EJS0.8.0 package/solver data remain in the inventoried payload.
Actual runtime paths (both health reports also contain all config/data paths):

- Portable ffmpeg: `D:\下载测试\YouTube视频\B4_3 Portable UTF8 验证\MediaDownloader-Portable\bin\ffmpeg.exe`
- Portable ffprobe: `D:\下载测试\YouTube视频\B4_3 Portable UTF8 验证\MediaDownloader-Portable\bin\ffprobe.exe`
- Portable quickjs: `D:\下载测试\YouTube视频\B4_3 Portable UTF8 验证\MediaDownloader-Portable\bin\runtime\qjs.exe`
- Installer ffmpeg: `D:\下载测试\YouTube视频\B4_3 安装目录\bin\ffmpeg.exe`
- Installer ffprobe: `D:\下载测试\YouTube视频\B4_3 安装目录\bin\ffprobe.exe`
- Installer quickjs: `D:\下载测试\YouTube视频\B4_3 安装目录\bin\runtime\qjs.exe`

[Portable results](evidence/b4_3/portable-results.json),
[Portable health](evidence/b4_3/portable-summary.json),
[Portable cookie/proxy fixtures](evidence/b4_3/portable-host-fixtures.json),
[Portable restart](evidence/b4_3/portable-restart-persistence.json),
[Installed results](evidence/b4_3/installer-results.json),
[Installed health](evidence/b4_3/installer-summary.json),
[Installed cookie/proxy fixtures](evidence/b4_3/installer-host-fixtures.json).

## Crash, lifecycle, standard uninstall

Actual installed download force-stop: observed PID2188 and2,096,128 partial
bytes, active persisted history row; taskkill /PID observed /T /F. Restart
preserves settings, reads valid JSON, recovers history to cancelled, Runtime
Health READY. Cancel/retry resumes past1 MiB. History51→52 for the interrupted
row. No unrelated process was selected. This is local installed evidence.
[Crash recovery](evidence/b4_3/installer-crash-crash-recovery.json).

Two actual normal visible-window starts on this existing host,0.482/0.999 s
in the fresh lifecycle run, with forced termination/restart; history55 records
unchanged, settings persist, all terminal states. New Chinese/space218-character
output exists (17,241,501 bytes); temporarily absent QuickJS is reported without
startup crash, then original file restored. These timings are not clean/cold-
cache benchmarks. [Lifecycle](evidence/b4_3/installer-lifecycle-lifecycle.json).

Final Setup installs current-user with requested Start Menu and desktop
shortcuts; the Windows token is not elevated. Actual application execution
never requests administrator privileges. Standard Inno uninstaller exit0:
program directory, both shortcuts and uninstall registry key removed. User
settings/history and six completed download file SHA256 hashes unchanged.
[Uninstall](evidence/b4_3/installer-uninstall-verified.json).

Normal final app/native process snapshot contained no MediaDownloader,
FFmpeg, FFprobe, qjs or Deno processes. Portable directory deletion in a true
independent environment remains NOT TESTED; no clean PASS inferred from this
local process snapshot or previous automation policy limitation.

## Actual packaging, grants, source materials and hashes

Final common payload1334 files,78 EXE/DLL/PYD,1347 embedded PYZ modules,
160 license-material files. Actual installed Setup files and actual ZIP bytes
match common payload SHA256 for every file. Portable adds portable.flag;
installer additionally generates unins000.exe/unins000.dat.
[ZIP/installed equality](evidence/b4_3/installer-artifacts.json),
[final artifact/native/source validation](evidence/b4_3-final-artifact-validation.json).

Removed Deno/old BtbN/ffplay/Chromaprint/FFTW components and their component-only
source/notices do not remain in final bundle. Qt optional Mesa software renderer
was already absent and remains absent. Actual LLVM compiler-runtime code is
now separately inventoried, with original compiler-rt/libc++/libc++abi/libunwind,
MinGW-w64 and Winpthreads texts. Native source pins/config/objects/static relink
materials accompany the binary; source-offer does not invent future undertakings.
Required known direct native grants/notices are retained; final Qt/Microsoft
combined-work/downstream terms remain professional review, not declared PASS.
No complete transitive target-wheel SBOM is fabricated.

| Artifact | Final bytes | SHA256 |
|---|---:|---|
| MediaDownloader-Portable.zip | 249637159 | fd722b494469e4ddda7c3b604759e09599e6b8e14d4ead1fe12033f976c5c415 |
| MediaDownloader-Setup.exe | 237696616 | aa34f3fba9eddbd6b6662f34f2c773072039db6375d2c3edefe8a5bf341be8d7 |

Both final SHA256 values and kit copies were reverified. Expanded payload:
488778232→312590344 bytes; native bin283575072→18647040 bytes.
Portable274131685→249637159 bytes. Setup230935228→237696616 bytes: newly
supplied source/relink materials increase Setup size despite much smaller
native runtime. File/licenses count is not forced downward by omitting grants
or source materials. [Exact inventory](B4_3_DISTRIBUTION_INVENTORY.md).

The self-contained release-test kit has ZIP, Setup, checksums, read-only
clean_machine_test.ps1, checklist and MediaDownloader-Test.wsb. WSB maps only
release-test read-only; no developer source checkout is mounted. Save/extract
under guest C:\Acceptance, not the read-only mapping. No usable independent
environment is available. Collector's real local run says NOT VERIFIED /
NOT TESTED, records host installed/PATH tools and does not install dependencies,
change PATH/security, terminate apps or invent functional PASS.
[Local collector scope](evidence/b4_3/local-collector-report.json).

## Tests and failures retained

Previous141 + new10 = **151 PASS,0 skip,19.850 seconds**.
`python -m unittest discover -s tests -p "test_*.py" -v`.
[Exact unittest output](evidence/b4_3/unit-tests.txt).
New checks exercise actual QuickJS/native capabilities, thumbnail/explicit
encoders, UTF-8 native health, no system JS fallback, native/source pin identity,
relink archive materials, removed components, independent Qt DLLs, actual ZIP
source/notices and restricted Sandbox mapping. Integration runs are separate,
not added to unittest totals. Final successful build log:
D:\YouTube视频下载\B4_3-build-utf8-final.log.

The new artifact checks require `build_windows.py` to have produced the final
payload first; missing build artifacts are failures, not skipped release evidence.

Preserved unsuccessful candidates: outer Git version leakage, dynamic pthread
import, omitted thumbnail WebP/JPEG support, and the first frozen UTF-8 health
failure. First frozen media cases completed but final health raised TypeError;
those entire runs are failed, not rewritten as PASS. Corrected final runs
above have final health/path/persistence evidence and exit0. Earlier transient
HTTP403 and a shipping metadata SSL EOF were resolved by fresh metadata/native
retry; no core retry algorithm change. Sanitized candidate reports are retained
under evidence/b4_3; raw logs stay in the test workspace, without Cookie values
or signed metadata URLs being copied into distribution reports.

## Still open

| Severity | Count | Item | Public release impact |
|---|---:|---|---|
| P0 | 0 | no observed final native/frozen core regression | none demonstrated |
| P1 Technical | 0 | all required technical build/runtime/regression checks passed | technical gate PASS |
| P1 Distribution | 2 | independent clean Windows acceptance; professional Qt/PySide/Microsoft final distribution-term review (Inno commercial business review included separately) | prevent overall/public PASS |
| P2 | 2 | inherited YouTube/challenge/Chromium auth limitations; older-player AV1/VP9/Opus support | no new runtime feature change |
| P3 | 1 | inherited partial language switching | no B5 polish |

Qt source/shared DLL replacement facts are supplied for professional review:
LGPLv3 combined-work/replacement/relink/source correspondence terms and wheel
incorporated-code attribution scope. Microsoft review concerns actual VC DLL
supplier downstream Distributable Code conditions, not a generic string match.
Inno commercial-license review is separate business work; the retained grant
permits commercial use and the official site requests a commercial license.
No entitlement or binding legal conclusion is asserted.

Stop after the requested commit. No B5, branding or v1.0/public release.
