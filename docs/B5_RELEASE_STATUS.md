# B5 Release Status

Product: **Media Downloader 0.9.0-rc1**. **B5 Result=PASS; Internal RC=READY**.
This unsigned internal candidate is not stable v1.0 or approval for public release.

| Gate | Status | Meaning |
|---|---|---|
| Technical Release Gate | PASS | Product polish, 151 old + 16 new tests, frozen Portable/Installer regression and final file checks passed |
| Clean Machine Gate | NOT TESTED | No independent Sandbox/VM/clean PC result; developer-host PATH isolation does not satisfy this gate |
| Public Distribution Gate | NEEDS LEGAL REVIEW | Inherited Qt/PySide6/Microsoft downstream terms and separate Inno commercial review remain pending |

The latest B5 scope explicitly allows an internal RC while the two distribution gates remain open.
B4.4's historical result is preserved. No legal conclusion, public release/tag or v1.0 publication is made.

| Severity | Count | Status |
|---|---:|---|
| P0 | 0 | No known B5 blocker |
| P1 Technical | 0 | Final local technical checks passed |
| P1 Distribution | 2 | Independent Windows acceptance; professional distribution review |
| P2 | 2 | Inherited upstream/authentication limitations and older-player codec support |
| P3 | 0 | Navigation-only language coverage replaced by full product catalogs/bindings |

## Known limitations and external actions

1. Chrome/Edge browser cookies remain experimental on Windows; Firefox is best effort. cookies.txt is supported.
2. YouTube 403/authentication/challenge failures remain possible; no guaranteed-access claim is made.
3. AV1/VP9/Opus may require a compatible player; no codec pack installation or silent downgrade occurs.
4. Run the rebuilt release-test kit and existing B4.4 checklist on independent Windows.
5. Obtain the pending distribution review, including the accurately packaged new Qt translation materials.
6. English/Simplified Chinese are supported; Traditional Chinese/RTL/accessibility certification are deferred.
7. Native Windows file-dialog chrome may follow OS language; supplied titles/filters are localized.

Final artifacts include bilingual README, local About/Help, notices, LICENSES, SOURCES, checksums,
release-manifest and RELEASE_NOTES_0.9.0-rc1.md. Original authors and third-party grants remain retained.
No telemetry, analytics or automatic crash/log upload was introduced.

Exact source-build identity and evidence: [B5_RC_VALIDATION.md](B5_RC_VALIDATION.md).
The completion commit adds reports/evidence/test tools; the release manifest names the preceding actual
product-code build commit. These commits serve different purposes and are not represented as identical.

Stop after this internal RC. Do not publish v1.0 or start new features.
