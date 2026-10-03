# B3 UI Architecture

Date: 2026-10-02. Branch: `codex/b3-ui-integration`.
Base: `ec9c2950ecdb487455dd090470835ce95650e51e` (B2).

B3 integrates the existing Windows desktop runtime, B1 records/services and B2
selector. No additional dependency, platform, package installer or branding work
was introduced. `core/format_selector.py` and `core/ffmpeg_utils.py` are unchanged.

## Runtime boundary

```text
MainWindow / DownloaderPage
  -> DownloadManager.quality_options / selection / prepare_download
  -> B2 normalize_formats / build_quality_options / select_quality
  -> FormatSelection
  -> option_builder.build_opts
  -> DownloadTask -> existing isolated yt-dlp runtime -> FFmpeg

Worker record callback -> DownloadBridge Qt signal -> main-thread widget slot
```

The UI binds a `FormatProfile` to each quality item. The recommended item binds
the `best` target. Labels are display text, never parsed to build expressions.
The Manager owns selection and option creation. Audio-only uses the B2 audio
target; Auto consumes the selector's final container. Explicit Custom Format
retains the existing advanced native expression path.

Single-video tasks retain their `FormatSelection`, rich quality label and option
snapshot. Playlist/batch entries resolve their own formats through the existing
B2 `QualitySelector` callback; the first video's IDs are never reused for another
URL. Retry creates a new task/worker and preserves the prior task's selection and
options within the current session.

## Pages and ownership

| Page | Implementation | Responsibility |
|---|---|---|
| Downloader | `gui/downloader_page.py` | URL, async thumbnail, metadata, bound quality, audio/container/path, read-only details |
| Queue | `gui/widgets/task_table.py` | Current-session records, progress, status, cancel/retry/remove/open-folder |
| History | `gui/history_page.py` | Persisted terminal records and file/folder/URL actions |
| Settings | Existing `SettingsPanel` | General, Download, Cookies, Proxy, FFmpeg, Advanced, Appearance; explicit Save |
| Logs | Existing `LogViewerWidget` | Redacted app logs, Clear View, Copy Selected, Open Log Folder |

`MainWindow` coordinates these pages through the existing Manager and services.
It does not instantiate `YoutubeDL`, execute FFmpeg, parse browser cookies/proxy
credentials, inspect raw yt-dlp progress hooks, or implement quality ranking.
The old settings dialog remains an extension compatibility holder. Its scroll
area relinquishes the settings widget before the new page takes ownership.

## Async and state handling

Analyze runs in the Manager executor and existing isolated runtime. A generation
token prevents a late response replacing a newer URL/auth context. URL or cookie,
profile, proxy, username/password, netrc changes invalidate analyzed selection.
Repeat Analyze, Download and Retry are guarded. Manager's active-URL protection
remains authoritative.

Worker callbacks only emit Qt signals. Decorated main-window slots update
widgets; logging uses a queued signal. No UI polling is used in production.
The acceptance harness timer measures the event loop; it is not app architecture.
Task statuses are exclusively the B1 canonical values. Display labels such as
Analyzing and Merging do not introduce serialized states.

Progress, speed, ETA, byte counts, title, quality and output path use record
snapshots. Raw formats are normalized in Core and displayed read-only separately
from the deduplicated primary dropdown. Thumbnail loading uses Qt Network with a
timeout and stale-reply cancellation; failure leaves a placeholder.

## Safety and persistence

The shared UI error mapper preserves typed failures and redacts expandable
details. Browser extraction failure recommends cookies.txt. Proxy/password inputs
are masked. The existing credentials/persistence services remove session secrets
from saved settings/history and redact logs. File/folder actions use native
`QDesktopServices` local URLs, without shell command construction.

Queue is session-scoped. History renders only completed/failed/cancelled records;
previous nonterminal history is marked cancelled on restart. Clearing history
preserves active records. Progress does not write history on each packet.
Settings use the existing JSON service and explicit Save; close persists saved
preferences plus geometry rather than unsaved credentials. Atomic JSON writes
remain Deferred (the underlying writer was not changed).

Closing with active tasks requests confirmation. Declining keeps the app open;
accepting invokes Manager cancellation/shutdown and aborts thumbnail work. Live
exit validation left zero child processes.
