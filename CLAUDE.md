# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```sh
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

FFmpeg must be on PATH — `app.py` checks and warns at startup if it's missing (`brew install ffmpeg` on macOS).

## Architecture

Two files do all the work:

- **`app.py`** — Flask backend with four routes:
  - `GET /` — serves the single-page UI
  - `POST /browse` — opens a native folder picker; on macOS uses `osascript` in a subprocess (tkinter crashes on macOS when called from a Flask worker thread, which is not the main thread); on other platforms runs tkinter in a subprocess for the same reason
  - `POST /download` — validates inputs, creates a `DownloadJob`, starts `run_download` in a `daemon=True` background thread, returns `job_id`
  - `GET /progress/<job_id>` — SSE stream that replays `job.events` at 150 ms intervals until status is `complete` or `error`

- **`templates/index.html`** — self-contained single-page UI (vanilla JS, no framework). Calls `/download`, then opens an `EventSource` to `/progress/<job_id>` and drives the progress bar from SSE events.

### Download flow

`run_download` calls `yt_dlp.YoutubeDL.download()` synchronously in the background thread. yt-dlp fires `progress_hooks` during download; the hook appends typed event dicts (`title`, `progress`, `complete`, `error`) to `DownloadJob.events` under a lock. The SSE generator in `/progress` reads those events and streams them as `data: <json>\n\n`.

yt-dlp downloads video and audio as separate streams then calls FFmpeg to merge them. The `phase` counter in `run_download` tracks which stream is active (0 = video, 1 = audio) so the UI can label each phase.

### Key constraints

- No playlist support — single video URLs only.
- `jobs` dict lives in process memory; restarting the server loses in-flight job state.
- yt-dlp format string: `bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best` with `merge_output_format: mp4`.
