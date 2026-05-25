import os
import shutil
import threading
import uuid
import time
import json

from flask import Flask, render_template, request, jsonify, Response
import yt_dlp

app = Flask(__name__)
jobs: dict[str, "DownloadJob"] = {}


def check_ffmpeg() -> None:
    path = shutil.which("ffmpeg")
    if path is None:
        print(
            "\n"
            "  WARNING: FFmpeg not found on PATH.\n"
            "  yt-dlp needs FFmpeg to merge video + audio into a single MP4.\n"
            "  Install it, then make sure 'ffmpeg' is on your system PATH.\n"
            "    macOS:   brew install ffmpeg\n"
            "    Windows: https://ffmpeg.org/download.html\n"
            "    Linux:   sudo apt install ffmpeg\n"
        )
    else:
        print(f"  FFmpeg: {path}")


class DownloadJob:
    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.status = "pending"   # pending | running | complete | error
        self.events: list[dict] = []
        self.lock = threading.Lock()

    def push(self, event_type: str, data: dict) -> None:
        with self.lock:
            self.events.append({"type": event_type, "data": data})


def run_download(job_id: str, url: str, save_path: str) -> None:
    job = jobs[job_id]
    job.status = "running"

    phase = [0]           # 0 = video stream, 1 = audio stream
    title_sent = [False]
    title_ref = [""]

    def progress_hook(d: dict) -> None:
        # Grab the video title from the first hook call that has it
        if not title_sent[0]:
            t = (d.get("info_dict") or {}).get("title", "")
            if t:
                title_ref[0] = t
                job.push("title", {"title": t})
                title_sent[0] = True

        status = d.get("status")

        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            percent = int(downloaded / total * 100) if total else 0
            speed = (d.get("_speed_str") or "").strip()
            eta = (d.get("_eta_str") or "").strip()
            phase_label = "Downloading video..." if phase[0] == 0 else "Downloading audio..."
            job.push("progress", {
                "percent": percent,
                "speed": speed,
                "eta": eta,
                "phase": phase_label,
            })

        elif status == "finished":
            phase[0] += 1
            job.push("progress", {
                "percent": 100,
                "speed": "",
                "eta": "",
                "phase": "Merging / converting...",
            })

    base_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
    }

    # Browsers to try for cookie extraction when YouTube returns 403.
    _BROWSERS = ["chrome", "firefox", "safari", "edge"]

    def _attempt(extra_opts: dict) -> None:
        opts = {**base_opts, **extra_opts}
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    def _is_403(exc: Exception) -> bool:
        return "403" in str(exc) or "Forbidden" in str(exc) or "Sign in" in str(exc)

    try:
        _attempt({})
    except yt_dlp.utils.DownloadError as exc:
        if not _is_403(exc):
            msg = str(exc)
            if "ERROR:" in msg:
                msg = msg.split("ERROR:", 1)[-1].strip()
            job.status = "error"
            job.push("error", {"message": msg})
            return

        # 403 — retry with each available browser's cookies
        succeeded = False
        for browser in _BROWSERS:
            try:
                # Reset phase/title state for the retry
                phase[0] = 0
                title_sent[0] = False
                _attempt({"cookiesfrombrowser": (browser,)})
                succeeded = True
                break
            except Exception:
                continue

        if not succeeded:
            job.status = "error"
            job.push("error", {"message": (
                "YouTube blocked the download (403). Make sure you're logged into "
                "YouTube in Chrome, Firefox, Safari, or Edge and try again."
            )})
            return

    except Exception as exc:
        job.status = "error"
        job.push("error", {"message": str(exc)})
        return

    title = title_ref[0] or "your video"
    job.status = "complete"
    job.push("complete", {"title": title})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/browse", methods=["POST"])
def browse():
    # tkinter crashes on macOS when called from a non-main thread (Flask worker).
    # Isolate the GUI call in a subprocess so it gets its own main thread.
    try:
        import subprocess
        import sys
        import platform

        if platform.system() == "Darwin":
            # osascript is simpler and more reliable than tkinter on macOS
            r = subprocess.run(
                ["osascript", "-e",
                 'POSIX path of (choose folder with prompt "Select Save Folder")'],
                capture_output=True, text=True, timeout=60,
            )
            folder = r.stdout.strip().rstrip("/") if r.returncode == 0 else ""
        else:
            script = (
                "import tkinter as tk, sys;"
                "from tkinter import filedialog;"
                "root = tk.Tk(); root.withdraw(); root.wm_attributes('-topmost', 1);"
                "f = filedialog.askdirectory(title='Select Save Folder');"
                "root.destroy(); print(f or '', end='')"
            )
            r = subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True, text=True, timeout=60,
            )
            folder = r.stdout.strip()

        return jsonify({"path": folder or ""})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/download", methods=["POST"])
def start_download():
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()
    save_path = (data.get("save_path") or "").strip()

    if not url:
        return jsonify({"error": "No URL provided."}), 400
    if not save_path:
        return jsonify({"error": "No save folder specified."}), 400
    if not os.path.isdir(save_path):
        return jsonify({"error": f"Folder not found: {save_path}"}), 400
    if not os.access(save_path, os.W_OK):
        return jsonify({"error": f"Cannot write to: {save_path}"}), 400

    job_id = str(uuid.uuid4())
    job = DownloadJob(job_id)
    jobs[job_id] = job

    t = threading.Thread(target=run_download, args=(job_id, url, save_path), daemon=True)
    t.start()

    return jsonify({"job_id": job_id})


@app.route("/progress/<job_id>")
def stream_progress(job_id: str):
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404

    def generate():
        job = jobs[job_id]
        sent = 0
        while True:
            with job.lock:
                new_events = list(job.events[sent:])
                status = job.status

            for ev in new_events:
                sent += 1
                yield f"data: {json.dumps(ev)}\n\n"

            if status in ("complete", "error"):
                break

            time.sleep(0.15)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    print("\nYouTube to MP4 Downloader")
    print("=" * 40)
    check_ffmpeg()
    print("\nOpen http://localhost:5000 in your browser.\n")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
