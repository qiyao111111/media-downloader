# B3 User Flow

## Single video

```text
Paste URL -> Analyze -> Metadata -> Quality Selection -> Container
-> Save Path -> Download -> Queue -> Postprocessing -> Completed
```

1. Paste a YouTube URL. Multiline input accepts one URL per line and removes
   duplicate entries. Empty input disables Analyze and Download.
2. Analyze changes to Analyzing and disables repeated requests. Extraction runs
   outside the GUI thread. Failed extraction leaves Download disabled and shows
   a readable message with redacted technical details.
3. Inspect title, uploader/channel, duration and highest source profile.
   Missing metadata uses Unknown; thumbnail failure is independent of extraction.
4. Leave Best Quality (Recommended), or select a real bound B2 profile. The
   dropdown has no hardcoded 4K/8K ceiling. Read-only Advanced Details shows IDs,
   dimensions/FPS/range/codecs/size and recommended container plus raw profiles.
5. Leave Auto to use B2's container recommendation. An override differing from
   the recommendation displays a compatibility notice and recommends Auto/MKV.
   Normal highest-quality downloads only copy/mux streams. Recode remains an
   explicit existing Advanced choice, never an automatic compatibility fix.
6. Select an existing Save To directory with Browse, including Chinese paths.
   Filename templates remain in Settings; yt-dlp performs filename sanitization.
7. Download creates the task using the Manager-produced selection/options and
   opens Queue. Repeat clicks do not create duplicate active tasks.
8. Queue shows record-based quality/status/progress/speed/ETA/bytes. Unknown
   totals use indeterminate progress. FFmpeg work displays Post-processing /
   Merging rather than 100% Downloading. Completed offers Open Folder and is
   also added to terminal History.

Changing URL or authentication settings requires another Analyze. Existing
queued tasks retain the snapshot from submission. Settings Save also invalidates
the previous preview, so the next download is analyzed with the saved context.

## Audio and advanced mode

Audio Only disables video quality selection and uses B2 best audio selection.
Best Audio preserves the original audio stream; MP3, M4A and Opus are explicit
existing extraction/conversion choices. Main video options do not rank audio.

Advanced -> Custom yt-dlp Format accepts an explicit expression. A nonempty
expression enables advanced mode and disables the normal quality selector. Clear
it to restore dynamic Best Quality. The ordinary flow never exposes format IDs
as its primary choices.

## Playlist and batch

Analyze a playlist to see its title/count and Download All. Each entry resolves
its own best source formats. Multiline URL submission creates distinct tasks;
additional URLs use independent B2 selection. B3 adds no large-playlist filtering
or selection system. A one-entry real public playlist completed through this UI.
Multi-entry presentation and multiline task isolation are additionally tested
with controlled data. Shorts/Live use existing yt-dlp handling without new UI.

## Failure, cancel and retry

Failed tasks show Failed, a diagnostic tooltip and Retry. The error dialog uses
the common mapper and redacted Details; it does not present a traceback. Browser
cookie failures recommend cookies.txt, and Windows Chrome/Edge remain
Experimental. Readable proxy, missing FFmpeg and format failures use the same
flow.

Cancel / Cancel All call the Manager, never kill a process from the UI. Cancelled
is terminal and cannot later become Completed. Remove on an active row first
requests cancellation and retains tracking until it finishes. Retry on
Failed/Cancelled creates a fresh worker; retained partial files can resume.
The old terminal entry remains in History. Across an app restart, historical
Retry uses current settings because secret task options are not persisted.

History supports Open File, Open Folder, Copy URL, Retry for failed/cancelled and
Remove History. Queue and History are distinct views. Settings expose separate
download concurrency and fragment concurrency, retries, cookies path/profile,
masked proxy URLs, FFmpeg/FFprobe detection, theme and navigation language.
Save applies settings consistently. JavaScript Runtime is explicitly Deferred.

Closing while active asks whether to cancel and exit. No leaves the app running;
Yes uses existing cleanup. Logs offer local viewing/copying only, with redaction
and no upload action.
