# B5.1 design system — accepted UI

The restored draft on `codex/b5-1-ui-polish` now uses one semantic QSS template and native Qt controls. The r2 baseline reconciliation is commit `dbd429367bc82db4d33fb4219a9496c23740b86d`; RC1 tag remains `e9f7d023cf90970b55ebcdfa34f6f376f9f1af9e`. UI commit is `6b41f84595d9da00cc746eacb4b41f891e706496`; RC2 was built from `af9949a35e53b1b27d4416010e639ac9187dd596`.

- Typography: Segoe UI, with Microsoft YaHei UI for Chinese. Page 24, section 17, body 13, secondary 12, caption 11 logical pixels. Logs use Consolas 12. No bundled font.
- Spacing: 4/8/12/16/20/24/32. Page padding 24 horizontal/20 vertical; card padding and gaps 16. Sidebar 200; page content capped at 1440.
- Radius: controls 6, navigation/chips/thumbnail 8 or 6, cards 12. Controls 32/40/44; Analyze, Download and Save render at least 44px after QSS padding/border sizing.
- Colors: background, surface, hover, selected, text, secondary, disabled, border, divider, accent/hover/pressed, success, warning, danger, info, on-accent. Both palettes are in `gui/design_tokens.py`.
- Buttons: primary Analyze/Retry, Download and Save; secondary utility actions; destructive actions use the danger text color. Download remains pinned outside the scrolling body.
- Inputs: native focus outlines, disabled appearance, masked proxy/password fields. URL failure uses a red border and an inline reason; the same analysis button becomes Retry.
- Cards: URL group, video information and configuration. The title takes at most two lines, byline elides, and chips consume existing B2 profiles.
- Queue: a stable table, two explicit lines for title/quality, an 8px progress track and integer percentage, one state-dependent main action. Completed size comes from the final local file, avoiding the previous last-audio-stream byte count. Compact columns retain Cancel/Retry/Open Folder visibility; full titles and quality remain in tooltips.
- Empty states: a compact centered icon/title/description group. Runtime rows pair name/version with a dot and a text status.
- About: native dialog with a scrolling content area and pinned Close, constrained to its parent height.

Unused old light/dark QSS files were removed. Popup, menu, tooltip, native palette, scrollbar and dialog colors now use the shared theme. Measured primary text, secondary text, primary button and status-badge color pairs exceed 4.5:1 in both themes; see `evidence/b5_1/contrast.json`. This is color-pair verification, not a full accessibility certification.

The baseline minimum stays 720x440. A hard 1100x680 logical minimum would exceed a 1366x768 desktop at 150% scaling. At compact sizes, body content scrolls and the primary action remains visible. Qt scaling acceptance covers 100/125/150%; changing Windows display settings and native DWM chrome remains outside this local check.
