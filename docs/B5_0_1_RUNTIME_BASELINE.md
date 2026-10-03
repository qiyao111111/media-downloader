# B5.0.1 official runtime baseline

B5.0.1 baseline reconciliation: PASS. Selected FFmpeg/FFprobe: 8.1.3-g330caae0c1-md-b43-r2.

Recipe, revision, configuration, exact lock hashes, source/build/relink materials, bundled binaries, inventories, release manifests and test expectations are aligned. The existing r2 artifacts were audited, not rebuilt or relabeled as a new application version. The application executable is unchanged; its original build_commit remains in the release manifest with the runtime_patch provenance. Both dist/release and release-test artifacts match manifest hashes; stale tracked release-test manifest/checksums are synchronized. Version remains 0.9.0-rc1. Stable tag remains immutable at e9f7d023cf90970b55ebcdfa34f6f376f9f1af9e. Historical B4/B5 r1 reports describe those historical builds and are not the current baseline definition.

## Validation

- Former failures: 2/2 PASS; exact hash checks retained, FFmpeg/FFprobe exact version equality and receipt/config equality strengthened.
- Previous tests: 167/167 PASS. New chapter embedding regression: 1/1 PASS. Total: 168 PASS, 0 FAIL.
- Real source application launch: existing --validate-release runner instantiated/showed the actual MainWindow with an isolated settings/history profile, using existing Analyze/Download buttons and Manager.
- Frozen application launch: copied unchanged executable with junctions to the exact bundled _internal/bin, portable flag and isolated profile; --validate-release exited successfully with no worker children. Runtime Health confirms FFmpeg/FFprobe r2 and QuickJS 0.17.0 READY. This is local-host launch validation, not a clean machine test.
- Real remote source: YouTube E86EwGT_c2M. 1080P selected 399+251, 8K Best Quality selected 571+251, Best Audio selected 251. All three downloads completed. Full output duration approximately 154.774 seconds; no trimming, simulation, source substitution or re-encoding was used.
- 1080P: video+audio download, merge/postprocessing/completed states, ffprobe and full decode PASS. Output 47,913,472 bytes.
- 8K: 7680x4320 AV1 + Opus; download/merge/ffprobe/full decode PASS. Output 614,003,521 bytes; Best Quality remains 4320P.
- Best Audio: Opus-only output, ffprobe and full decode PASS.
- All three full decodes: exit 0, error output 0 bytes. End-of-stream confirmed for both video decodes.
- Encoder/muxer source configuration did not change; existing encoder/conversion tests remain in the full suite. Additional all-format audio conversion smoke was not required by the demuxer-only change.

Evidence: evidence/b5_0_1/provenance.json; full-tests.txt; two-tests.txt; frozen-launch/summary.json; smoke/results.json and all three ffprobe JSONs; 1080-decode.json; 8k-decode.json; audio-decode.json; accompanying progress/error outputs.

P0: 0. P1 technical baseline mismatch: 0.
Clean Machine Gate: NOT TESTED. Public Distribution Gate: NEEDS LEGAL REVIEW.

## UI draft handoff

After the baseline fix commit, return to codex/b5-1-ui-polish, cherry-pick that commit, pop the protected stash and verify every tracked/untracked Git blob against ui-draft-preservation.json. Run the entire suite before any further UI work. Restoration/test evidence will be recorded separately after that handoff. Do not continue B5.1 visual acceptance or create an RC2 tag in this task.
