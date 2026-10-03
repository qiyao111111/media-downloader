# B5.1 visual validation — PASS within local Qt scope

Actual Qt windows were shown before further implementation. Initial captures under `build/b51-initial` were reviewed in both themes across all five pages, About and seven Settings categories. The restored draft was preserved; fixes addressed cropped icons, button sizing, focus presentation, empty states, repeated status text, refresh leftovers, long titles and compact dialogs.

| Desktop | Qt scale | Themes | Languages | Result |
|---|---|---|---|---|
| 1366x768 | 1 / 1.25 / 1.5 | Light / Dark | zh_CN / en_US | PASS |
| 1920x1080 | 1 / 1.25 / 1.5 | Light / Dark | zh_CN / en_US | PASS |

`tests/validate_b5_1_visual.py` starts separate QApplication processes with `QT_SCALE_FACTOR`. It uses physical desktop dimensions minus native frame/taskbar allowance, records actual logical sizes and device scale, shows every page and category, and asserts no horizontal overflow on Downloader, Settings or active Queue. The pinned Download button is at least 44 logical pixels and remains inside the window. About fits the parent; content can scroll. Exact 1366x768 and 1920x1080 client sizes also pass the Qt geometry test.

Matrix metadata is in `evidence/b5_1/geometry-matrix.json`; captures are in `screenshots/b5_1/dpi`. These are actual widget renders with explicitly synthetic long-title/8K60 fixtures for layout stress. They are separate from real-source captures. Native Windows DPI setting changes, DWM chrome, dragging/snap and independent clean Windows acceptance were not performed.

Real-source screenshots use the actual metadata and thumbnail for `E86EwGT_c2M`. Its quality controls include 1080P, 4K and 8K. `hVvEISFw9w0` produces actual 4320P/60 FPS/AV1/HDR10 chips. Unknown range is covered by a Qt fixture and does not acquire SDR/HDR labels. Queue downloading/postprocessing/completed captures were taken during real downloads, and cancel/retry captures during actual button actions. History reads the resulting persisted records. Logs captures include actual runtime health text; an extra capture demonstrates its empty state.

Reviewed required captures: Downloader Light/Dark and analyzed Light/Dark; downloading/completed Queue; History; General/Runtime/Cookies Settings; Logs; About. Additional reviewed captures cover compact active Queue, Chinese text, dark quality popup/menu, error Retry and constrained About. Padding, alignment, title bounds, focus, primary actions, badge appearance, text contrast and scrolling were inspected. All required images are real application/widget screenshots; none is a mockup or generated design image.

Invalid URL uses a real Analyze extraction. Network failure and HTTP 403 use typed-error presentation injection, clearly recorded in `persistence-errors.json`; they are not live server-failure tests. Error details remain available in the existing safe dialog. Dark/English persist across separate processes, and Missing Keys = 0.

RC2 frozen Portable and installed-mode payload screenshots confirm actual 0.9.0-rc2 About text and both languages with unchanged source-quality selection. These are in `screenshots/b5_1/rc2`; Settings uses the category-aware source matrix. Setup was built, not freshly reinstalled.

Clean Machine Gate: NOT TESTED. Public Distribution Gate: NEEDS LEGAL REVIEW.
