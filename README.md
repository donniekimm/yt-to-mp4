# YouTube to MP4 Downloader

A simple web app that runs on your computer and lets you download YouTube videos as MP4 files. No account or subscription needed — just open it in your browser like a website.

---

## Before You Start

You need two free tools installed. You only do this once.

### 1. Homebrew (Mac only — skip if you already have it)

Homebrew is an installer that makes everything else easier. Open **Terminal** and paste this:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Python

```sh
brew install python@3.12
```

### 3. FFmpeg

FFmpeg is what combines the video and audio into a single MP4 file.

```sh
brew install ffmpeg
```

---

## Running the App

**The first time:**

1. Download or clone this project to your computer.
2. Open **Terminal**, navigate to the project folder, and run:

```sh
./run.sh
```

This automatically installs everything the app needs and starts it. It may take a minute the very first time.

**Every time after that**, just run the same command:

```sh
./run.sh
```

**Then open your browser and go to:**

```
http://localhost:5000
```

---

## How to Use It

1. Paste a YouTube video URL into the **YouTube URL** field.
2. Click **Browse…** to choose where to save the file.
3. Click **Download MP4** and watch the progress bar.
4. Your file is saved as `Video Title.mp4` in the folder you picked.

---

## Troubleshooting

**"403 Forbidden" error** — YouTube blocked the download. Make sure you're logged into YouTube in Chrome, Firefox, Safari, or Edge, then try again. The app will automatically use your browser's login to get through.

**"FFmpeg not found" warning in the terminal** — Run `brew install ffmpeg` and restart the app.

**Playlists don't work** — Paste a single video URL, not a playlist link.
