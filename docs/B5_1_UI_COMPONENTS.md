# B5.1 UI components — accepted

Shared widgets live in `gui/widgets/presentation.py`. No dependency was added.

| Component | Use |
|---|---|
| StatusBadge | Queue and History status cells; existing state values retained |
| QualityChip | Highest-quality metadata from B2 profiles; equal height, font, spacing and padding |
| InfoChip | Best Quality/cookies.txt Recommended and browser support indicators |
| EmptyStateWidget | Queue, History and Logs icon/title/description |
| RuntimeStatusRow | yt-dlp, FFmpeg, FFprobe and QuickJS from actual health results |
| InfoBanner | Cookies warning, with safe readable contrast |
| TaskProgressBar | Existing range/value API, 8px track and separate percentage/merging text |
| PrimaryButton / SecondaryButton | About actions and common styling |
| TwoLineLabel / ElidedLabel | Bounded title and uploader/duration display with full tooltips |
| ThumbnailLabel | Rounded downloaded thumbnail |
| Local SVG line icons | Navigation and empty states, recolored with theme |

History reuses existing badges on refresh. Superseded chips and runtime rows hide before deferred deletion; underlying legacy status-cell text stays available to callers but renders transparent. These fixes prevent duplicate or misplaced labels during refresh.

The selector, Manager, queue state machine, record model, option collector, persistence services and FFmpeg baseline were not changed. Settings keeps the existing controls and keys across seven categories. Proxy stays a masked URL control; adding protocol/host/port controls would expand the existing draft and is deferred. Completed Open File is in the context menu; Open Folder is the main row action. Failed/cancelled tasks expose Retry and context-menu Remove.

The 28 new Qt contracts cover themes/popups, translation, source quality and unknown range, state presentation, empty states, categories/values, secret masking, runtime/About, bounded titles, geometry and display regressions. See `test_b5_1_visual.py` and the regression report.
