# Recording capability audit

Audited on 2026-10-29 on the student's Windows 11 laptop, before any recording was made.
Only capabilities that were actually found and used are claimed.

## What exists and what was used

| Capability | Found? | Used? | Notes |
|---|---|---|---|
| Computer-control tool (Claude clicking the real desktop) | **No** - not offered in this session | No | So nothing in the videos is a mouse-driven GUI session. |
| FFmpeg 9.0.2 (full build) with `gdigrab` window capture, `libx264` | Yes | **Yes** | Records one named window to H.264 MP4. |
| OBS Studio | Installed (`C:\Program Files\obs-studio`) | No | Needs a person to operate its GUI; FFmpeg does the same job from a script. |
| Windows Terminal / console | Yes | **Yes** | A dedicated console window (`conhost`) with a large font is recorded. |
| Chrome and Edge | Yes | Where a browser is needed | Selenium-driven Chrome (see `capture_ui.py`). |
| Microphone (Realtek array) | Yes | No | There is no person speaking during a scripted run. |
| Windows text-to-speech (SAPI voices David, Zira) | Yes | **Yes** | Synthetic voice-over. **Not a human recording.** |
| Docker Desktop | Installed, **was stopped** | Started by me | `docker 29.7.2`. Only hotel-project containers are touched. |
| Jenkins (`hotel-jenkins-jenkins-1`) | Container exists, **was stopped** (7 days) | Started when a task needs it | UI at `http://localhost:8090`, user `admin`. |
| Local registry (`hotel-jenkins-registry-1`) | Container exists, stopped | Started with Jenkins | `localhost:5000`. |
| Python `.venv` (Flask 3.1.3, Selenium 4.51, pytest, flake8) | Yes | **Yes** | The project's own interpreter. |
| Ansible controller image `hotel-ansible:latest`, lab image `hotel-ansible-lab-target` | Yes | Tasks 13-14 | Container-based lab, not a separate VM. |
| Maven / Java build | Maven **not installed** | No | The project is Python; see Task 3 about the build-tool question. |

## How the videos are made (and what that means)

1. `_tools/record-demo.ps1` opens a **new console window** (large Consolas font, black background).
2. Inside it `_tools/player.ps1` types each command and **runs it for real**; the real output stays on
   screen. Nothing is pre-recorded or simulated.
3. `ffmpeg` (gdigrab) captures **only that window** (by its title). Other windows, notifications, the
   desktop and the taskbar are not recorded, so nothing private can leak in.
4. A voice-over is generated offline by Windows text-to-speech and mixed in at the exact moment each
   step starts. The same text is shown on screen (yellow) and saved as an SRT subtitle file.
5. Screenshots are single frames cut from the finished video, so they are genuine.

## Honest limits

- The voice is a **synthetic computer voice**. If you want your own voice, record yourself with
  Windows Voice Recorder while reading `task-NN-narration.md` and replace the audio track, or just
  present the video with your own live commentary.
- There is **no mouse pointer** and no clicking, because the recordings are scripted terminal and
  browser-window sessions rather than a person using the desktop.
- Windows that need a login (Jenkins UI, GitHub) are not recorded with typed credentials. For those, the
  tasks use the real Jenkins API/CLI output or existing genuine evidence, and the status file says which.
- Videos that depend on Docker/Jenkins show whatever state the machine was in when recorded.

## Why not just use OBS?

OBS would also work, but it has to be started and stopped by hand and records whatever is on the
screen, which includes your notifications and other windows. The scripted window capture is
repeatable: if a command output changes, run the recorder again and the video is rebuilt.
