import os
import shutil
import threading
import uuid
import time
import json
import tempfile
import glob

from flask import Flask, render_template, request, jsonify, Response, send_file
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
        )
    else:
        print(f"  FFmpeg: {path}")


class DownloadJob:
    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.status = "pending"   # pending | running | complete | error
        self.events: list[dict] = []
        self.lock = threading.Lock()
        self.tmp_dir: str | None = None
        self.file_path: str | None = None
        self.created_at: float = time.time()

    def push(self, event_type: str, data: dict) -> None:
        with self.lock:
            self.events.append({"type": event_type, "data": data})


def _cleanup_old_jobs() -> None:
    while True:
        time.sleep(300)
        cutoff = time.time() - 1800  # 30 minutes
        for job_id in list(jobs.keys()):
            job = jobs.get(job_id)
            if job and job.created_at < cutoff:
                if job.tmp_dir:
                    shutil.rmtree(job.tmp_dir, ignore_errors=True)
                jobs.pop(job_id, None)


threading.Thread(target=_cleanup_old_jobs, daemon=True).start()


def run_download(job_id: str, url: str) -> None:
    job = jobs[job_id]
    job.status = "running"
    tmp_dir = tempfile.mkdtemp(prefix=f"ytdl_{job_id}_")
    job.tmp_dir = tmp_dir

    phase = [0]
    title_sent = [False]
    title_ref = [""]

    def progress_hook(d: dict) -> None:
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

    opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "outtmpl": os.path.join(tmp_dir, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as exc:
        msg = str(exc)
        if "ERROR:" in msg:
            msg = msg.split("ERROR:", 1)[-1].strip()
        job.status = "error"
        job.push("error", {"message": msg})
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return
    except Exception as exc:
        job.status = "error"
        job.push("error", {"message": str(exc)})
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return

    mp4_files = glob.glob(os.path.join(tmp_dir, "*.mp4"))
    if mp4_files:
        job.file_path = mp4_files[0]

    title = title_ref[0] or "your video"
    job.status = "complete"
    job.push("complete", {"title": title})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def start_download():
    data = request.get_json(force=True, silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "No URL provided."}), 400

    job_id = str(uuid.uuid4())
    job = DownloadJob(job_id)
    jobs[job_id] = job

    t = threading.Thread(target=run_download, args=(job_id, url), daemon=True)
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


@app.route("/file/<job_id>")
def serve_file(job_id: str):
    job = jobs.get(job_id)
    if not job or job.status != "complete" or not job.file_path:
        return jsonify({"error": "File not ready"}), 404
    if not os.path.exists(job.file_path):
        return jsonify({"error": "File no longer available"}), 410

    return send_file(
        job.file_path,
        as_attachment=True,
        download_name=os.path.basename(job.file_path),
        mimetype="video/mp4",
    )


if __name__ == "__main__":
    print("\nYouTube to MP4 Downloader")
    print("=" * 40)
    check_ffmpeg()
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"
    print(f"\nOpen http://localhost:{port} in your browser.\n")
    app.run(host=host, port=port, debug=False, threaded=True)
