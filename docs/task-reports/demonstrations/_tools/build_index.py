"""Write README.md (master index) and GENERATION_STATUS.md from what really exists on disk.

    .venv\\Scripts\\python docs/task-reports/demonstrations/_tools/build_index.py

A video is listed as recorded only if the .mp4 file exists and ffprobe can read it. The
hand-written facts (what is live vs historical evidence, manual steps) come from status.json.
"""
import json
import re
import subprocess
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMOS = HERE.parent
REPORTS = DEMOS.parent
STATUS = json.loads((HERE / "status.json").read_text(encoding="utf-8"))


def probe(mp4):
    if not mp4.exists():
        return None
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                        "-of", "json", str(mp4)], capture_output=True, text=True)
    try:
        info = json.loads(r.stdout)
        dur = float(info["format"]["duration"])
        kinds = {s["codec_type"] for s in info["streams"]}
    except Exception:
        return None
    return {"seconds": dur, "audio": "audio" in kinds, "mb": mp4.stat().st_size / 1e6}


def mmss(sec):
    return f"{int(sec) // 60}:{int(sec) % 60:02d}"


def title_of(n):
    f = next(REPORTS.glob(f"task-{n:02d}-*.md"), None)
    if f:
        t = f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
        return re.sub(r"^Task \d+\s*-\s*", "", t)
    return f"Task {n}"


def rel(path):
    return path.relative_to(DEMOS).as_posix()


def collect():
    rows = []
    for n in range(1, 16):
        t = f"{n:02d}"
        d = DEMOS / f"task-{t}"
        video = d / f"task-{t}-demo.mp4"
        info = probe(video)
        parts = sorted(d.glob(f"task-{t}-*-demo.mp4"))
        shots = len(list((d / "screenshots").glob("*.png"))) if (d / "screenshots").exists() else 0
        st = STATUS.get(str(n), {})
        rows.append({
            "n": n, "t": t, "title": title_of(n), "dir": d, "video": video, "info": info,
            "parts": parts, "shots": shots,
            "narr": (d / f"task-{t}-narration.md").exists(),
            "cmds": (d / f"task-{t}-commands.md").exists(),
            "qs": (d / f"task-{t}-questions.md").exists(),
            "srt": (d / f"task-{t}-demo.srt").exists(),
            "st": st,
        })
    return rows


def video_cell(r):
    if r["info"]:
        a = "voice-over (synthetic) + subtitles" if r["info"]["audio"] else "no audio"
        return f"[task-{r['t']}-demo.mp4](task-{r['t']}/task-{r['t']}-demo.mp4) - {mmss(r['info']['seconds'])}, {a}"
    if r["parts"]:
        return f"parts recorded, not joined yet ({len(r['parts'])})"
    return "NOT RECORDED"


def build_readme(rows):
    out = ["# Demonstration pack - all 15 tasks", "",
           "Videos, narration scripts, command sheets, viva questions and screenshots for the 15 tasks of the",
           "**CI/CD pipeline for a Hotel Room Booking Portal**. Everything here was produced by running the",
           "real project; see [recording-capability-audit.md](recording-capability-audit.md) for how, and",
           "[GENERATION_STATUS.md](GENERATION_STATUS.md) for what is finished, what is live and what must be done by you.", "",
           "## The project in one paragraph", "",
           "A small hotel (6 rooms) needs a web portal where guests register, see free rooms for their dates, request,",
           "confirm and cancel bookings and track the status (Python + Flask + SQLite, layered controller / service / DAO).",
           "The DevOps half makes every change safe: Git branches and tags, a Jenkins pipeline (lint, unit, integration and",
           "Selenium tests as a quality gate), Docker images tagged with version and commit, a local registry, deployment",
           "with Docker Compose, and Ansible to provision a server, re-run idempotently and roll back to an earlier release.", "",
           "## How to use this pack", "",
           "1. Watch the task's video once. The yellow text on screen is the narration; the same words are in `task-NN-narration.md`.",
           "2. Repeat the commands from `task-NN-commands.md` yourself (they run in order, from the project folder).",
           "3. Practise the answers in `task-NN-questions.md`.",
           "4. If something is not running, the recovery table at the end of the command sheet tells you what to start.", "",
           "## Master index", "",
           "| # | Task | Video (path, length, audio) | Narration | Commands | Viva questions | Screenshots | Demonstration status | Remaining manual steps |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        t = r["t"]
        link = lambda ok, name: f"[{name}](task-{t}/{name})" if ok else "missing"  # noqa: E731
        shots = f"[screenshots/](task-{t}/screenshots/) ({r['shots']})" if r["shots"] else "none"
        out.append("| {n} | {title} | {video} | {narr} | {cmds} | {qs} | {shots} | {status} | {manual} |".format(
            n=r["n"], title=r["title"], video=video_cell(r),
            narr=link(r["narr"], f"task-{t}-narration.md"), cmds=link(r["cmds"], f"task-{t}-commands.md"),
            qs=link(r["qs"], f"task-{t}-questions.md"), shots=shots,
            status=r["st"].get("status", "not started"), manual=r["st"].get("manual", "-")))
    out += ["", "Other files: [recording-capability-audit.md](recording-capability-audit.md), "
            "[GENERATION_STATUS.md](GENERATION_STATUS.md), `_tools/` (the recorder and generators; re-run a recording with "
            "`_tools/record-demo.ps1 -TaskId NN`).", ""]
    return "\n".join(out)


def build_status(rows):
    done = [r for r in rows if r["info"]]
    out = ["# Generation status", "", f"Last updated: {date.today().isoformat()}", "",
           f"**Videos recorded and checked: {len(done)} of 15.**", ""]
    out += ["| # | Task | Video | Evidence type | Notes |", "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['n']} | {r['title']} | {'RECORDED ' + mmss(r['info']['seconds']) if r['info'] else 'not recorded'} "
                   f"| {r['st'].get('evidence', '-')} | {r['st'].get('notes', '')} |")
    out += ["", "## Evidence type, in plain words", "",
            "- **live**: the commands / browser actions in the video were executed for real while recording.",
            "- **live + historical**: a live part, plus saved output from an earlier real run (the video says which).",
            "- **historical**: the video displays genuine saved evidence (build logs, screenshots); nothing was re-run.", ""]
    out += ["## What you must start yourself before showing the project", ""]
    out += [f"- {x}" for x in STATUS.get("_manual_start", [])]
    out += ["", "## Things found while preparing this pack (not changed by me)", ""]
    out += [f"- {x}" for x in STATUS.get("_findings", [])]
    out += ["", "## Environment state while recording", ""]
    out += [f"- {x}" for x in STATUS.get("_environment", [])]
    out += ["", "## How to resume", "",
            "Re-run a task: `powershell -ExecutionPolicy Bypass -File docs\\task-reports\\demonstrations\\_tools\\record-demo.ps1 -TaskId NN [-Part name]`,",
            "then `.venv\\Scripts\\python docs/task-reports/demonstrations/_tools/join_parts.py NN` (multi-part tasks),",
            "`build_support_files.py NN` and finally `build_index.py` to refresh this file and the README.", ""]
    return "\n".join(out)


def main():
    rows = collect()
    (DEMOS / "README.md").write_text(build_readme(rows), encoding="utf-8")
    (DEMOS / "GENERATION_STATUS.md").write_text(build_status(rows), encoding="utf-8")
    print(f"index written; {sum(1 for r in rows if r['info'])} of 15 videos present and readable")


if __name__ == "__main__":
    main()
