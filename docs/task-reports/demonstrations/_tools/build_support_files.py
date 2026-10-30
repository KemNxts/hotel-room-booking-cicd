"""Generate narration / command-sheet / viva files for one task from its steps files.

    .venv\\Scripts\\python docs/task-reports/demonstrations/_tools/build_support_files.py 01

A task is recorded as one video (task-NN-steps.json) or as several parts
(task-NN-<part>-steps.json, e.g. 'app' and 'git' for Task 6) that are joined
into task-NN-demo.mp4 afterwards. The same steps files are what the recorder
executes, so these documents always match the video.

Reads  task-NN/task-NN[-part]-steps.json
       task-NN/task-NN[-part]-demo.timing.json (written by record-demo.ps1, optional)
       ../task-NN-*.md             (existing task report: section G = viva questions)
Writes task-NN-narration.md, task-NN-commands.md, task-NN-questions.md
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMOS = HERE.parent
REPORTS = DEMOS.parent


def mmss(sec):
    sec = int(sec)
    return f"{sec // 60:02d}:{sec % 60:02d}"


def duration(mp4):
    if not mp4.exists():
        return 0.0
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0


def load_parts(task):
    d = DEMOS / f"task-{task}"
    files = sorted(d.glob(f"task-{task}*-steps.json"))
    parts, offset = [], 0.0
    for f in files:
        part = f.name[len(f"task-{task}"):-len("-steps.json")].strip("-")
        sfx = f"-{part}" if part else ""
        demo = json.loads(f.read_text(encoding="utf-8"))
        tf = d / f"task-{task}{sfx}-demo.timing.json"
        timing = json.loads(tf.read_text(encoding="utf-8-sig")) if tf.exists() else None
        parts.append({"part": part, "demo": demo, "timing": timing, "offset": offset})
        offset += duration(d / f"task-{task}{sfx}-demo.mp4")
    return d, parts


def report_title(task, fallback):
    report = next(REPORTS.glob(f"task-{task}-*.md"), None)
    if report:
        first = report.read_text(encoding="utf-8").splitlines()[0]
        return first.lstrip("# ").strip()
    return fallback


def narration(task, parts, title):
    n = int(task)
    out = [f"# Task {n} - narration script", "", f"**{title}**", "",
           "Read this aloud (or let the video's voice-over do it). The voice-over in the video is a",
           "synthetic Windows text-to-speech voice, not a human recording. Each step has the four",
           "parts: what I am doing, why, what the output means, and one sentence for the professor.", ""]
    k = 0
    for p in parts:
        if len(parts) > 1:
            out += [f"# Part: {p['demo']['title']}", ""]
        for i, s in enumerate(p["demo"]["steps"]):
            k += 1
            stamp = ""
            if p["timing"] and i < len(p["timing"]["steps"]):
                stamp = f" [video {mmss(p['offset'] + p['timing']['steps'][i]['videoStartSec'])}]"
            out += [f"## Step {k} - {s['title']}{stamp}", ""]
            if s.get("cmd"):
                out += ["**What I am doing:** running", "", "```powershell", s["cmd"], "```", ""]
            elif s.get("action"):
                out += [f"**What I am doing:** {s['action']}", ""]
            out += ["**Spoken script (as in the video):**", "", f"> {s.get('say', '')}", ""]
            if s.get("expect"):
                out += [f"**What the output means:** {s['expect']}", ""]
            if s.get("tell"):
                out += [f"**What I will tell the professor:** \"{s['tell']}\"", ""]
    return "\n".join(out)


def commands(task, parts, title):
    n = int(task)
    out = [f"# Task {n} - command sheet", "", f"**{title}**", ""]
    out += ["## Before you start", ""]
    seen = set()
    for p in parts:
        for item in p["demo"].get("prereq", []):
            if item not in seen:
                seen.add(item)
                out.append(f"- {item}")
    if not seen:
        out.append("- Open PowerShell in the project folder.")
    out += ["", "Working directory for every command:", "",
            "```powershell", r"cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING", "```", ""]
    out += ["## Commands in the order they are run in the video", ""]
    k = 0
    for p in parts:
        if len(parts) > 1:
            out += [f"### {p['demo']['title']}", ""]
        out += ["| # | Step | Command / action | Expected result |", "|---|---|---|---|"]
        for s in p["demo"]["steps"]:
            k += 1
            what = s.get("cmd") or s.get("action")
            if not what:
                continue
            what = what.replace("|", "\\|").replace("\n", "<br>")
            out.append(f"| {k} | {s['title']} | `{what}` | {s.get('expect', '').replace('|', '/')} |")
        out.append("")
    out += ["Note: the recorder prepends `.venv\\Scripts` to PATH, so `pytest` and `python` mean the",
            "project's virtual-environment versions. In your own terminal use `.venv\\Scripts\\pytest`",
            "(or activate with `.venv\\Scripts\\Activate.ps1`). Variables such as `$c` or `$s` are set by an",
            "earlier step, so run the steps of one part in the same PowerShell window and in order.", ""]
    extras = [e for p in parts for e in p["demo"].get("extra", [])]
    if extras:
        out += ["## Extra commands (not recorded, for your own practice)", ""]
        for e in extras:
            out += [f"- {e['what']}:", "", "  ```powershell", f"  {e['cmd']}", "  ```", ""]
    out += ["## If something is not running (recovery)", ""]
    out += ["| Symptom | What to do |", "|---|---|"]
    for p in parts:
        for r in p["demo"].get("recovery", []):
            out.append(f"| {r['symptom']} | {r['fix']} |")
    out += ["", "Re-record with:", "", "```powershell"]
    for p in parts:
        part_arg = f" -Part {p['part']}" if p["part"] else ""
        out.append(rf"powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId {task}{part_arg}")
    out += ["```", ""]
    return "\n".join(out)


def questions(task, parts, title):
    n = int(task)
    report = next(REPORTS.glob(f"task-{task}-*.md"), None)
    out = [f"# Task {n} - viva questions and answers", "", f"**{title}**", ""]
    body = ""
    if report:
        text = report.read_text(encoding="utf-8")
        m = re.search(r"^## G\..*?\n(.*?)(?=^## H\.)", text, re.S | re.M)
        if m:
            body = m.group(1).strip()
    if body:
        out += [f"Source: section G of [{report.name}](../../{report.name}) - answers checked against the",
                "repository and the evidence in this project.", "", body, ""]
    else:
        out += ["(No questions found in the task report - add them here.)", ""]
    extra = [q for p in parts for q in p["demo"].get("extraQuestions", [])]
    if extra:
        out += ["## Extra questions that match this demonstration", ""]
        for i, q in enumerate(extra, 1):
            out += [f"{i}. **{q['q']}**", f"   {q['a']}", ""]
    return "\n".join(out)


def main():
    task = sys.argv[1].zfill(2)
    d, parts = load_parts(task)
    title = report_title(task, parts[0]["demo"]["title"])
    (d / f"task-{task}-narration.md").write_text(narration(task, parts, title), encoding="utf-8")
    (d / f"task-{task}-commands.md").write_text(commands(task, parts, title), encoding="utf-8")
    (d / f"task-{task}-questions.md").write_text(questions(task, parts, title), encoding="utf-8")
    print(f"task-{task}: wrote narration, commands, questions ({len(parts)} part(s))")


if __name__ == "__main__":
    main()
