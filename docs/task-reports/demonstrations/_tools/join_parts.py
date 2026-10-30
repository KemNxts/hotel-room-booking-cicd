"""Join the recorded parts of one task into task-NN-demo.mp4 (+ merged .srt).

    .venv\\Scripts\\python docs/task-reports/demonstrations/_tools/join_parts.py 06

Parts are the files task-NN-<part>-demo.mp4 (e.g. 'app' and 'git' for Task 6), joined in
alphabetical order of the part name. Every part is scaled to fit a 1440x900 canvas (black
bars if the shape differs) so that terminal parts and browser parts can sit in one video.
The subtitle files are shifted by the length of the parts before them and merged.
"""
import re
import subprocess
import sys
from pathlib import Path

DEMOS = Path(__file__).resolve().parent.parent
W, H, FPS = 1440, 900, 15


def duration(mp4):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout.strip()
    return float(out)


def srt_time(t):
    h, rem = divmod(int(t * 1000), 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt_time(text):
    h, m, rest = text.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def merge_srt(srts_with_offsets, out):
    cue, lines = 1, []
    for srt, offset in srts_with_offsets:
        text = srt.read_text(encoding="utf-8-sig")
        for block in re.split(r"\r?\n\r?\n", text.strip()):
            parts = block.strip().splitlines()
            if len(parts) < 3:
                continue
            a, b = parts[1].split(" --> ")
            lines += [str(cue), f"{srt_time(parse_srt_time(a) + offset)} --> {srt_time(parse_srt_time(b) + offset)}",
                      *parts[2:], ""]
            cue += 1
    out.write_text("\n".join(lines), encoding="utf-8")
    return cue - 1


def main():
    task = sys.argv[1].zfill(2)
    d = DEMOS / f"task-{task}"
    parts = sorted(d.glob(f"task-{task}-*-demo.mp4"))
    if not parts:
        sys.exit(f"no part recordings found in {d}")
    out = d / f"task-{task}-demo.mp4"
    inputs, filters, labels = [], [], []
    for i, p in enumerate(parts):
        inputs += ["-i", str(p)]
        filters.append(
            f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,"
            f"setsar=1,fps={FPS}[v{i}];[{i}:a]aresample=44100[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    fc = ";".join(filters) + ";" + "".join(labels) + f"concat=n={len(parts)}:v=1:a=1[v][a]"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex", fc,
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", str(out)]
    subprocess.run(cmd, check=True)

    offsets, t = [], 0.0
    for p in parts:
        srt = p.with_suffix(".srt")
        if srt.exists():
            offsets.append((srt, t))
        t += duration(p)
    cues = merge_srt(offsets, d / f"task-{task}-demo.srt")
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
                           "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout.strip()
    print(f"task-{task}: joined {len(parts)} parts -> {out.name}  ({info}; {cues} subtitle cues)")
    for p in parts:
        print(f"   part {p.name}  {duration(p):.1f}s")


if __name__ == "__main__":
    main()
