# B3 UI State Matrix

Task state values are the B1 enum. Idle and Analyzing below are preview view
conditions, not new serialized task states. Analyze/Download are controlled by
the current preview; Queue actions are controlled independently per task.

| State | Analyze Button | Download Button | Cancel | Retry | Quality Selector | Progress |
|---|---|---|---|---|---|---|
| Idle | Enabled with URL | Disabled | No task | No task | Disabled | Empty state |
| Analyzing | Disabled, Analyzing… | Disabled | Existing tasks only | Existing terminal tasks only | Disabled | Loading text |
| Ready | Enabled | Enabled with valid selection/path | Existing tasks only | Existing terminal tasks only | Enabled for video | Metadata/details |
| Queued | Enabled if preview idle | Submitted URLs guarded | Enabled | Disabled | Current preview may be edited | 0% |
| Downloading | Enabled if preview idle | Submitted URLs guarded | Enabled | Disabled | Current preview may be edited | 0–100% or indeterminate, speed/ETA/bytes |
| Postprocessing | Enabled if preview idle | Submitted URLs guarded | Enabled | Disabled | Current preview may be edited | Merging…; speed/ETA -- |
| Completed | Enabled | Re-Analyze to resubmit same URL | Disabled | Disabled | Current preview rules | 100%; Open Folder |
| Failed | Enabled | Re-Analyze or Retry | Disabled | Enabled once per old task | Current preview rules | Last value; diagnostic error |
| Cancelled | Enabled | Re-Analyze or Retry | Disabled | Enabled once per old task | Current preview rules | Last value |

The transient task `parsing` is displayed as Analyzing; `ready` is displayed as
Ready. `queued`, `downloading`, `postprocessing`, `completed`, `failed`,
`cancelled` retain their canonical serialized values. Playlist processing may
cycle from postprocessing to downloading for the next entry under B1 policy.

## Additional guards

- Audio Only, Custom Format and Playlist disable the video selector.
- Empty/invalid path, failed/stale preview or missing selection disable Download.
- Missing URL disables Analyze. A running Analyze cannot be repeated.
- Auth/URL changes invalidate old preview. Late generation results are ignored.
- Cancel All is disabled for an empty or entirely terminal Queue.
- Retry disables its row button during submission; Manager rejects active URL
  duplication. A successful retry removes the old Queue row and keeps History.
- Completed Open Folder requires an output path. History Retry is only available
  for failed/cancelled records; file/folder actions require recorded output.
- Total unknown uses indeterminate progress only while downloading. Unknown ETA
  is --; known ETA is MM:SS or HH:MM:SS. Speed uses KB/MB/GB per second.
- Closing active tasks defaults to No; accepting invokes Manager cleanup.

Tests: `tests/test_b3_ui.py`, real Queue events in
`tests/validate_b3_desktop.py`, cancellation/active-exit lifecycle in
`tests/validate_b3_lifecycle.py`.
