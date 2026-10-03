# Media Downloader 0.9.0-rc2

Internal Release Candidate. This build completes B5.1 visual polish based on the existing desktop UI draft.

Clean Machine Gate: NOT TESTED
Public Distribution Gate: NEEDS LEGAL REVIEW

## Changes

- Fluent-inspired desktop presentation with shared typography, spacing, colors, native controls and Light/Dark palettes.
- Downloader improvements: clear URL/Analyze focus, bounded video title, source-quality chips, Recommended quality, inline errors/Retry and a pinned Download action.
- Queue clarity: title/quality, an 8px progress bar, integer percentage, speed/ETA, status badges and actions appropriate to the task state. Completed size reflects the final file.
- Settings organization: seven categories, aligned rows, browser-cookie support badges and runtime name/version/status rows.
- Consistent empty states, readable Logs, local About/Help and Chinese font fallback. Compact windows scroll while retaining primary actions.
- No core download-selection, queue-policy or persistence changes. Best Quality still uses the B2 selector.
- FFmpeg/FFprobe baseline remains `8.1.3-g330caae0c1-md-b43-r2`, including the previously reconciled chapter-metadata fix. yt-dlp and QuickJS remain pinned.

## Validation and limits

168 previous tests and 28 new Qt tests passed. Live GUI checks cover 1080P completion, 4K/8K quality options, 8K60 HDR10 metadata, MP3, Cancel/Retry, history, settings and theme/language restart. Complete 1080P/audio/retry outputs decoded without errors. 8K60 HDR download/color fidelity is not claimed.

Both languages and themes were exercised at two desktop sizes and 100/125/150% Qt scaling. Native Windows display-setting/DWM checks and independent clean Windows acceptance remain pending.

Chrome/Edge cookie extraction is experimental, Firefox is best effort, and cookies.txt remains recommended. Upstream authentication/challenge/403 behavior and older-player AV1/VP9/Opus compatibility remain limitations.

Portable and Installer include third-party notices, license texts and source/relink materials. Professional distribution-term review remains pending. No RC2 tag is created by this stage. This candidate is unsigned and is not a stable or production release.

Do not share cookies.txt. Only download content you have the right to save or use. No telemetry or automatic log upload is added.
