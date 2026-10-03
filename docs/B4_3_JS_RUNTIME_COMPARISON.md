# B4.3 JavaScript runtime A/B

Windows 11 Pro 10.0.26200 AMD64; yt-dlp 2026.8.19; yt-dlp-ejs 0.8.0.
No challenge solver or format selector changes. Both runtimes are explicitly
selected through yt-dlp's native js_runtimes API (`quickjs:<absolute qjs path>`
is the corresponding CLI syntax).

| Runtime | Fixed source | Preview seconds | Formats | Best selection | Result |
|---|---|---:|---:|---|---|
| Deno 2.9.7 | E86EwGT_c2M | 3.572 | 53 | 571+251; 7680×4320 AV1 30 SDR | PASS |
| QuickJS-NG 0.17.0 | E86EwGT_c2M | 3.775 | 53 | same | PASS |
| Deno 2.9.7 | hVvEISFw9w0 | 5.373 | 70 | 702+140; 7680×4320 AV1 60 HDR10 | PASS |
| QuickJS-NG 0.17.0 | hVvEISFw9w0 | 3.960 | 70 | same | PASS |

Normalized video format lists are exactly equal for both fixed sources.
Timing is a single observed network/cache run, not a performance guarantee.
Fresh native web_safari/mweb EJS provider probes observed Deno and QuickJS
respectively: 40 formats each, zero challenge errors; 9.879 versus 15.540 s.
This separate challenge probe uses metadata only, including missing-PO-token
format metadata, and does not represent successful streaming of those formats.
Normal download tests use normal clients and actual accessible streams.

Evidence: [metadata comparison](evidence/b4_3/js-comparison.json),
[provider probe](evidence/b4_3/js-challenge-probe.json),
[Deno network](evidence/b4_3/deno-network-network-results.json),
[QuickJS network](evidence/b4_3/quickjs-network-network-results.json).
Real Qt/MainWindow A/B on the existing frozen EXE also completed full 1080P
and 8K60/HDR metadata with each explicit runtime override; final B4.3 bundle
validation is recorded separately in the release gate report.

QuickJS is an own build of official QuickJS-NG 0.17.0 revision
6d46d07d04041b40f4f49eaa7fdebe44c314c699. Official source archive SHA256:
92212ea9a257a387a35abca50505d59ad9edddba4580e064929d396511b89dcf.
Binary SHA256 c6f2427ca3f9f1b45cd616ab92f6c49036957590a793afc1fa7526bd441bcddb;
LLVM-MinGW 20260922 UCRT / Clang 23.1.2; static CLI, mimalloc disabled.
[Exact build pins](../build/native-runtime-lock.json),
[build recipe](../build_native_runtime.py), official
[QuickJS-NG project](https://github.com/quickjs-ng/quickjs/tree/6d46d07d04041b40f4f49eaa7fdebe44c314c699).
Original MIT license, contributor notices and exact source accompany the RC.

Decision: bundled QuickJS. Deno and its Deno-only materials are removed from
actual release payload; explicit developer Deno overrides remain unsupported
for first-version product use. No automatic system/Deno fallback. EJS remains
bundled independently; remote_components stays empty. Native PE imports show
only Windows OS runtime dependencies, not an extra JS engine DLL distribution.

Failures are preserved rather than rewritten: initial challenge-driver
attempts used clients that did not invoke a provider; one forced web attempt
returned no normal formats. The corrected probe records actual provider use.
One CDN HTTP 403 in media/proxy trials passed after fresh metadata extraction;
failed attempt logs remain outside the reports, with redacted summaries where
recorded. No credential values or signed format URLs are copied here.
