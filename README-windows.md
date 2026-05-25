# YouTube to MP4 Downloader — Windows & Linux

A simple web app that runs on your computer and lets you download YouTube videos as MP4 files. No account or subscription needed — just open it in your browser like a website.

---

## Windows

### Before You Start

You need two free tools installed. You only do this once.

#### 1. Python

1. Go to [python.org/downloads](https://www.python.org/downloads/) and click **Download Python**.
2. Run the installer. **Important:** on the first screen, check the box that says **"Add Python to PATH"** before clicking Install.

#### 2. FFmpeg

1. Go to [ffmpeg.org/download.html](https://ffmpeg.org/download.html), click **Windows**, then download a build from **gyan.dev** (the "release" zip).
2. Unzip it somewhere permanent, like `C:\ffmpeg`.
3. Add FFmpeg to your PATH so Windows can find it:
   - Press `Windows + S`, search for **"Environment Variables"**, and open it.
   - Under **System Variables**, click **Path → Edit → New**.
   - Add the path to the `bin` folder inside your FFmpeg folder, e.g. `C:\ffmpeg\bin`.
   - Click OK on all windows.
4. Open a new Command Prompt and type `ffmpeg -version` to confirm it works.

### Running the App

**The first time:**

1. Download or clone this project to your computer.
2. Open **Command Prompt**, navigate to the project folder, and double-click `run.bat` — or run it from Command Prompt:

```bat
run.bat
```

This automatically installs everything the app needs and starts it. It may take a minute the very first time.

**Every time after that**, just double-click `run.bat` or run the same command.

**Then open your browser and go to:**

```
http://localhost:5000
```

---

## Linux

### Before You Start

Open a terminal and run the following based on your distribution. You only do this once.

**Ubuntu / Debian:**
```sh
sudo apt update
sudo apt install python3 python3-venv ffmpeg
```

**Fedora / RHEL:**
```sh
sudo dnf install python3 ffmpeg
```

### Running the App

**The first time:**

1. Download or clone this project to your computer.
2. Open a terminal, navigate to the project folder, and run:

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

**"FFmpeg not found" warning in the terminal** — FFmpeg isn't installed or isn't on your PATH. Follow the FFmpeg setup steps above and restart the app.

**Playlists don't work** — Paste a single video URL, not a playlist link.

**Windows: the Command Prompt window closes immediately** — Right-click `run.bat` and choose **"Run as administrator"**, or open Command Prompt first and run it from there so you can see any error messages.
