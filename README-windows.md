# YouTube to MP4 Downloader — Windows Setup

A simple web app that runs on your computer and lets you download YouTube videos as MP4 files.

---

## Step 1 — Install Python (one-time)

1. Go to **python.org/downloads** and click **Download Python**.
2. Run the installer. On the first screen, **check the box that says "Add Python to PATH"** before clicking Install.

To confirm it worked, open **Command Prompt** and type:
```
python --version
```
You should see a version number.

---

## Step 2 — Install FFmpeg (one-time)

FFmpeg combines the video and audio into a single MP4 file. Without it, downloads won't work.

1. Go to **ffmpeg.org/download.html**, click **Windows**, then download a build from **gyan.dev** (the "release" zip).
2. Unzip the folder somewhere permanent — for example, rename it to `ffmpeg` and move it to `C:\ffmpeg`.
3. Add FFmpeg to PATH so Windows can find it:
   - Press `Windows + S`, search for **Environment Variables**, and open it.
   - Under **System Variables**, click **Path → Edit → New**.
   - Type `C:\ffmpeg\bin` and click OK on all windows.
4. Open a **new** Command Prompt and type `ffmpeg -version` to confirm it works.

---

## Step 3 — Run the App

1. Download this project and unzip it to a folder (e.g. your Desktop).
2. Open that folder in **File Explorer**.
3. Double-click **`run.bat`**.

The first time, it takes about a minute to set up. After that it starts immediately.

4. Open your browser and go to:
```
http://localhost:5000
```

**Every time after that**, just double-click `run.bat` again.

---

## How to Use It

1. Paste a YouTube URL into the **YouTube URL** field.
2. Click **Browse…** to choose where to save the file.
3. Click **Download MP4** and watch the progress bar.
4. Your file is saved as `Video Title.mp4` in the folder you picked.

---

## Troubleshooting

**The Command Prompt window closes immediately** — Open Command Prompt first, then drag `run.bat` into the window and press Enter. This keeps the window open so you can see the error.

**"FFmpeg not found"** — FFmpeg isn't installed or PATH wasn't set correctly. Redo Step 2 and open a fresh Command Prompt window before testing again.

**Playlists don't work** — Paste a single video URL, not a playlist link.

**Download fails or gives an error** — Some videos are restricted and can't be downloaded. Try a different video to confirm the app is working.
