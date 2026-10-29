"""Capture the screenshots used by docs/task-reports/.

Two kinds of evidence, both real:

1. Browser screenshots of running systems (the portal, Jenkins, the local
   registry, the public GitHub repository).
2. Terminal output: the command is really executed now, its raw output is
   saved as .txt next to the image, and the output is rendered as a PNG
   (dark "terminal" style). Every rendered image says in its footer that it
   is rendered from real output, with the command and capture time.
   Existing log files (e.g. Ansible runs) are rendered the same way and are
   labelled "rendered from log file ...".

Usage (repo root, services running):
    python scripts/capture_report_evidence.py --jenkins-password <admin password>
    python scripts/capture_report_evidence.py --only terminal      # or: browser
"""

import argparse
import base64
import html
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "docs" / "task-reports" / "assets"
RAW = ASSETS / "raw"
PY = str(REPO / ".venv" / "Scripts" / "python.exe") if os.name == "nt" else sys.executable
GITHUB = "https://github.com/KemNxts/hotel-room-booking-cicd"
RERENDER = False  # set by --rerender

TERMINAL_CSS = """
body { margin: 0; background: #0c0c0c; font-family: Consolas, 'Cascadia Mono', monospace; }
.bar { background: #2b2b2b; color: #ddd; font: 13px 'Segoe UI', sans-serif; padding: 8px 14px; }
.bar b { color: #fff; }
pre { margin: 0; padding: 14px 16px; color: #e6e6e6; font-size: 14px; line-height: 1.4;
      white-space: pre-wrap; word-break: break-word; }
.cmd { color: #f9f1a5; }
.ok { color: #7ee787; } .bad { color: #ff7b72; } .note { color: #8b949e; }
.foot { background: #1f1f1f; color: #9a9a9a; font: 12px 'Segoe UI', sans-serif; padding: 6px 14px;
        border-top: 1px solid #333; }
"""


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def browser(width=1280, height=900):
    o = webdriver.ChromeOptions()
    o.add_argument("--headless=new")
    o.add_argument(f"--window-size={width},{height}")
    o.add_argument("--hide-scrollbars")
    return webdriver.Chrome(options=o)


def full_page(drv, path, width=1280, max_height=3200, min_height=500, content_only=False):
    """Screenshot the whole page (viewport resized to the page height)."""
    drv.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": 900, "deviceScaleFactor": 1, "mobile": False},
    )
    time.sleep(0.4)
    # A short page reports at least the viewport height; for rendered terminal
    # pages measure the content itself so no empty space is captured.
    h = drv.execute_script(
        "return Math.ceil(document.body.getBoundingClientRect().height)"
        if content_only
        else "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
    )
    drv.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": max(min_height, min(h, max_height)),
            "deviceScaleFactor": 1,
            "mobile": False,
        },
    )
    time.sleep(0.5)
    path.parent.mkdir(parents=True, exist_ok=True)
    if content_only:
        # Chrome never makes a normal screenshot shorter than its window, so
        # capture exactly the content area through the DevTools protocol.
        clip = {"x": 0, "y": 0, "width": width, "height": max(min_height, min(h, max_height)), "scale": 1}
        shot = drv.execute_cdp_cmd("Page.captureScreenshot",
                                   {"format": "png", "captureBeyondViewport": True, "clip": clip})
        path.write_bytes(base64.b64decode(shot["data"]))
    else:
        drv.save_screenshot(str(path))
    print("saved", path.relative_to(REPO) if path.is_relative_to(REPO) else path)


def colour(line):
    esc = html.escape(line)
    if line.startswith("$ ") or line.startswith("PS> "):
        return f'<span class="cmd">{esc}</span>'
    low = line.lower()
    bad = (" failed", "failed ", "failure", "error:", "error ", "conflict (", "fatal:", "traceback")
    if any(w in low for w in bad) and "failed=0" not in low and not low.rstrip().endswith((".py", ".html")):
        return f'<span class="bad">{esc}</span>'
    if any(w in low for w in (" passed", "success", "healthy", "changed=0", "finished: success")):
        return f'<span class="ok">{esc}</span>'
    return esc


def render_text(drv, text, png, title, footer, width=1100):
    page = (
        f"<!doctype html><html><head><meta charset='utf-8'><style>{TERMINAL_CSS}</style></head><body>"
        f"<div class='bar'><b>{html.escape(title)}</b></div>"
        f"<pre>{chr(10).join(colour(line) for line in text.rstrip().splitlines())}</pre>"
        f"<div class='foot'>{html.escape(footer)}</div></body></html>"
    )
    tmp = Path(tempfile.mkdtemp()) / "t.html"
    tmp.write_text(page, encoding="utf-8")
    drv.get(tmp.as_uri())
    full_page(drv, png, width=width, max_height=6000, min_height=50, content_only=True)


def run(drv, task, name, title, cmds, cwd=REPO, env=None):
    """Run real commands now, save raw output (.txt) and a rendered PNG.

    With RERENDER set, the commands are NOT run again: the image is rebuilt from
    the saved .txt, and the footer keeps the original capture time (file mtime).
    """
    folder = ASSETS / f"task-{task:02d}"
    saved = folder / f"{name}.txt"
    if RERENDER and saved.exists():
        mtime = datetime.fromtimestamp(saved.stat().st_mtime, timezone.utc)
        captured = mtime.strftime("%Y-%m-%d %H:%M UTC")
        footer = (f"Rendered from real command output captured {captured} in {cwd.name}"
                  f"  |  raw text: {name}.txt")
        render_text(drv, saved.read_text(encoding="utf-8"), folder / f"{name}.png", title, footer)
        return
    out = []
    for cmd in cmds:
        out.append(f"$ {cmd}")
        res = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, **(env or {})},
        )
        out.append((res.stdout + res.stderr).rstrip())
        out.append("")
    text = "\n".join(out)
    folder = ASSETS / f"task-{task:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.txt").write_text(text, encoding="utf-8")
    render_text(
        drv,
        text,
        folder / f"{name}.png",
        title,
        f"Rendered from real command output captured {now()} in {cwd.name}  |  raw text: {name}.txt",
    )


def render_file(drv, task, name, title, source, start=None, stop=None, keep=None):
    """Render (part of) an existing real log file."""
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    if start is not None:
        lines = lines[start:stop]
    if keep:
        lines = [ln for ln in lines if keep(ln)]
    folder = ASSETS / f"task-{task:02d}"
    render_text(
        drv,
        "\n".join(lines),
        folder / f"{name}.png",
        title,
        f"Rendered from the real log file {source.relative_to(REPO).as_posix()} (unedited lines"
        f"{'' if not keep and start is None else ', excerpt'})",
    )


# ----------------------------------------------------------------- terminal


def terminal(drv):
    git_env = {"GIT_PAGER": "cat", "PAGER": "cat"}
    run(
        drv,
        3,
        "flask-routes",
        "PowerShell - Flask route list (controllers)",
        [f'"{PY}" -m flask --app wsgi routes --sort rule'],
    )
    run(
        drv,
        3,
        "project-structure",
        "PowerShell - layered application structure",
        ["git ls-files app tests | sort"],
        env=git_env,
    )
    run(
        drv,
        4,
        "git-branches-tags-remote",
        "Git - branches, tags and the GitHub remote",
        ["git branch -a --format=%(refname:short)", "git tag -n1", "git remote -v"],
        env=git_env,
    )
    run(
        drv,
        4,
        "git-main-history",
        "Git - release history of main and the first commit",
        [
            'git log --first-parent --format="%h %ad %s" --date=short main',
            (
                "git log --reverse --oneline --no-decorate develop | head -1"
                if os.name != "nt"
                else "git rev-list --max-parents=0 --abbrev-commit HEAD"
            ),
            'git show --stat --format="%h %ad %s" --date=short 541dad5',
        ],
        env=git_env,
    )
    run(
        drv,
        4,
        "gitignore-and-templates",
        "Git - .gitignore, .gitattributes and GitHub templates",
        [
            "git ls-files .github",
            "type .gitattributes" if os.name == "nt" else "cat .gitattributes",
            "type .gitignore" if os.name == "nt" else "cat .gitignore",
        ],
        env=git_env,
    )
    run(
        drv,
        5,
        "feature-branch-history",
        "Git - feature/security-hardening developed on its own branch and merged",
        [
            'git log --graph --format="%h %s" 475cecd..bdfc2fb',
            'git show --stat --format="%h %ad %s" --date=short 716b910',
        ],
        env=git_env,
    )
    run(
        drv,
        5,
        "all-feature-merges",
        "Git - every feature branch merged into develop with --no-ff",
        ['git log --merges --first-parent --format="%h %ad %s" --date=short develop'],
        env=git_env,
    )
    run(
        drv,
        6,
        "merge-conflict-resolution",
        "Git - the merge commit that resolved the real conflict",
        ['git log --graph --format="%h %s" da225fb..9e766ac', "git show --stat 9e766ac"],
        env=git_env,
    )
    run(
        drv,
        6,
        "release-tags",
        "Git - release tags v1.0.0 and v1.1.0",
        [
            "git tag -n1",
            "git log --oneline -1 v1.0.0",
            "git log --oneline -1 v1.1.0",
            "git cat-file -p v1.1.0",
        ],
        env=git_env,
    )
    run(
        drv,
        7,
        "jenkins-files",
        "PowerShell - local Jenkins definition (plugins, compose)",
        [
            "type deploy\\jenkins\\plugins.txt" if os.name == "nt" else "cat deploy/jenkins/plugins.txt",
            "docker compose -f deploy/jenkins/docker-compose.yml ps --format "
            '"table {{.Service}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"',
        ],
    )
    run(
        drv,
        8,
        "jenkinsfile-stages",
        "Git Bash - stages and parameters declared in the Jenkinsfile",
        [
            (
                'findstr /n /c:"stage(" /c:"choice(" /c:"string(name" /c:"pollSCM" Jenkinsfile'
                if os.name == "nt"
                else 'grep -n "stage(\\|choice(\\|string(name\\|pollSCM" Jenkinsfile'
            )
        ],
    )
    run(
        drv,
        9,
        "selenium-run",
        "PowerShell - Selenium journeys run locally with pytest",
        [f'"{PY}" -m pytest -m e2e -v -p no:cacheprovider'],
    )
    run(
        drv,
        9,
        "full-test-suite",
        "PowerShell - flake8 + the full test suite",
        [
            f'"{PY}" -m flake8 -j 1 app tests scripts wsgi.py gunicorn.conf.py && echo flake8: no findings',
            f'"{PY}" -m pytest -q -p no:cacheprovider tests/unit',
            f'"{PY}" -m pytest -q -p no:cacheprovider tests/integration',
            f'"{PY}" -m pytest -q -p no:cacheprovider tests/e2e',
        ],
    )
    run(
        drv,
        10,
        "defect-branch-history",
        "Git - the deliberate defect and the corrective commit (experiment branch)",
        [
            'git log --format="%h %s" -3 experiment/defect-demo',
            'git show 5844eec --stat --format="%h %s"',
            "git diff 5844eec~1 5844eec -- app/dao/booking_dao.py",
            "git branch --contains 5844eec",
        ],
        env=git_env,
    )
    run(
        drv,
        11,
        "docker-images-containers",
        "PowerShell - Docker images and running containers",
        [
            'docker image ls --format "table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}" '
            "--filter reference=*hotel*",
            'docker image ls --format "table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}" '
            "--filter reference=localhost:5000/*",
            'docker ps --format "table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}"',
            "docker volume ls --filter name=hotel",
        ],
    )
    run(
        drv,
        12,
        "deployed-versions",
        "PowerShell - which tested image each environment runs",
        [
            "docker ps --filter name=hotel-staging --filter name=hotel-prod "
            '--format "table {{.Names}}\\t{{.Image}}\\t{{.Status}}"',
            "curl -s http://localhost:8081/health",
            "curl -s http://localhost:8082/health",
            "curl -s http://localhost:5000/v2/_catalog",
            "curl -s http://localhost:5000/v2/hotel-booking-app/tags/list",
        ],
    )
    run(
        drv,
        13,
        "lab-server-state",
        "Docker - state of the lab server after the Ansible runs",
        [
            'docker compose -f deploy/ansible/lab/docker-compose.yml exec -T target sh -c "'
            "stat -c '%a %U %n' /opt/hotel-booking/.env /opt/hotel-booking/previous_release; "
            "cat /opt/hotel-booking/previous_release; ls /opt/hotel-booking; "
            "docker image ls --format '{{.Repository}}:{{.Tag}}' | grep hotel; "
            "docker ps --format '{{.Names}} {{.Image}} {{.Status}}'; systemctl is-enabled docker\""
        ],
    )
    run(
        drv,
        15,
        "all-environments-health",
        "PowerShell - health of every running environment",
        [
            "curl -s http://127.0.0.1:5001/health",
            "curl -s http://localhost:8081/health",
            "curl -s http://localhost:8082/health",
            "curl -s http://localhost:8088/health",
        ],
    )
    run(
        drv,
        15,
        "git-status-final",
        "Git - current branch and uncommitted work (honest state)",
        ["git branch --show-current", "git status --short", "git log --oneline -1"],
        env=git_env,
    )

    # Existing real logs, rendered.
    raw = RAW
    render_file(
        drv,
        8,
        "jenkins-build-11-console",
        "Jenkins build #11 console (excerpt)",
        raw / "jenkins-build-11.log",
        keep=lambda ln: any(
            k in ln
            for k in (
                "Building commit",
                "[Pipeline] { (",
                "passed",
                "sha256sum",
                "digest:",
                '"status"',
                "Deployed",
                "Finished",
                "flake8",
                "docker push",
                "compose up",
                "grep -q",
            )
        ),
    )
    ev = REPO / "docs" / "evidence" / "jenkins"

    def skip_lines(ln):
        keys = ("Building commit", "FAILED tests", "failed,", "skipped due", "Finished",
                "AssertionError: assert")
        return any(k in ln for k in keys)
    render_file(
        drv,
        10,
        "build-02-defect-console",
        "Jenkins build #2 console (excerpt) - deliberate defect",
        ev / "build-02-defect-fails.log",
        keep=skip_lines,
    )
    render_file(
        drv,
        10,
        "build-03-fix-console",
        "Jenkins build #3 console (excerpt) - after the fix",
        ev / "build-03-fix-green.log",
        keep=lambda ln: any(
            k in ln for k in ("Building commit", " passed", "Deployed", "Finished", '"status"')
        ),
    )
    render_file(
        drv,
        10,
        "build-09-rerun-console",
        "Jenkins build #9 console (excerpt) - defect re-run after report fix",
        ev / "build-09-defect-rerun-after-report-fix.log",
        keep=lambda ln: ("rm -rf reports" in ln) or skip_lines(ln),
    )
    render_file(
        drv,
        6,
        "merge-conflict-output",
        "Git - real merge conflict output (2026-10-11, original commit IDs)",
        REPO / "docs" / "evidence" / "git" / "merge-conflict.txt",
        stop=60,
    )
    lc = raw / "docker-lifecycle.txt"
    n = len(lc.read_text(encoding="utf-8").splitlines())
    render_file(
        drv,
        11,
        "lifecycle-part1-build-run",
        "Docker lifecycle demo, part 1: build, tag, run, ports, logs",
        lc,
        start=0,
        stop=n // 2,
    )
    render_file(
        drv,
        11,
        "lifecycle-part2-stop-restart-volume",
        "Docker lifecycle demo, part 2: stop, restart, remove, volume",
        lc,
        start=n // 2,
        stop=None,
    )
    for task, fname, title in (
        (
            13,
            "ansible-run1-first-deploy-v1.0.0",
            "Ansible run 1 - first provisioning of a fresh server (v1.0.0)",
        ),
        (14, "ansible-run2-upgrade-v1.1.0", "Ansible run 2 - upgrade to v1.1.0"),
        (14, "ansible-run3-repeat-idempotent", "Ansible run 3 - same playbook again: changed=0"),
        (14, "ansible-run4-rollback", "Ansible run 4 - rollback.yml back to v1.0.0"),
        (14, "ansible-run5-e2e-after-rollback", "Selenium journeys against the rolled-back server"),
    ):
        render_file(drv, task, fname, title, raw / f"{fname}.txt")


# ------------------------------------------------------------------ browser


def jenkins_login(drv, base, password):
    drv.get(f"{base}/login")
    WebDriverWait(drv, 20).until(EC.visibility_of_element_located((By.NAME, "j_username"))).send_keys("admin")
    drv.find_element(By.NAME, "j_password").send_keys(password)
    drv.find_element(By.NAME, "Submit").click()
    WebDriverWait(drv, 20).until(EC.presence_of_element_located((By.ID, "page-header")))


def page(drv, url, path, wait_css="body", settle=1.0, width=1280, max_height=3200):
    drv.get(url)
    WebDriverWait(drv, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_css)))
    time.sleep(settle)
    full_page(drv, path, width=width, max_height=max_height)


def browser_shots(drv, jenkins_password):
    a = ASSETS
    # GitHub (public, read-only)
    page(drv, GITHUB, a / "task-04" / "github-repository-home.png", "main", 2)
    page(drv, f"{GITHUB}/branches/all", a / "task-04" / "github-branches.png", "main", 2)
    page(drv, f"{GITHUB}/tags", a / "task-06" / "github-release-tags.png", "main", 2)
    page(drv, f"{GITHUB}/tree/main/.github", a / "task-04" / "github-templates-folder.png", "main", 2)
    page(drv, f"{GITHUB}/issues?q=", a / "task-02" / "github-issues-empty.png", "main", 2)
    page(drv, f"{GITHUB}/pulls?q=", a / "task-05" / "github-pull-requests-empty.png", "main", 2)
    page(
        drv,
        f"{GITHUB}/compare/develop...feature/nights-column",
        a / "task-05" / "github-compare-feature-branch.png",
        "main",
        3,
    )
    for task, doc in (
        (1, "01-problem-definition"),
        (2, "02-agile-plan"),
        (3, "03-srs-architecture"),
        (6, "04-git-workflow"),
        (15, "15-task-checklist"),
        (15, "08-project-report"),
    ):
        page(
            drv,
            f"{GITHUB}/blob/main/docs/{doc}.md",
            a / f"task-{task:02d}" / f"github-doc-{doc}.png",
            "main",
            6,
            max_height=5200,
        )
    for task, f in (
        (8, "Jenkinsfile"),
        (11, "Dockerfile"),
        (11, "docker-compose.yml"),
        (13, "deploy/ansible/playbook.yml"),
        (13, "deploy/ansible/inventory.ini"),
        (13, "deploy/ansible/group_vars/web.yml"),
        (14, "deploy/ansible/rollback.yml"),
        (9, "tests/e2e/test_journeys.py"),
        (3, "app/schema.sql"),
    ):
        page(
            drv,
            f"{GITHUB}/blob/main/{f}",
            a / f"task-{task:02d}" / f"github-file-{f.replace('/', '_')}.png",
            "main",
            3,
            max_height=5200,
        )

    # Running environments
    page(drv, "http://localhost:8082/rooms", a / "task-12" / "prod-portal-v1.1.0.png")
    page(drv, "http://localhost:8082/health", a / "task-12" / "prod-health.png")
    page(drv, "http://localhost:8081/health", a / "task-08" / "staging-health-after-build-11.png")
    page(drv, "http://localhost:5000/v2/hotel-booking-app/tags/list", a / "task-12" / "registry-tags.png")
    page(drv, "http://localhost:8088/rooms", a / "task-14" / "lab-server-after-rollback-v1.0.0.png")
    page(drv, "http://localhost:8088/health", a / "task-14" / "lab-server-health-after-rollback.png")

    # Jenkins
    base = "http://localhost:8090"
    jenkins_login(drv, base, jenkins_password)
    job = f"{base}/job/hotel-booking"
    page(drv, f"{job}/", a / "task-07" / "jenkins-job-stage-view.png", "#main-panel", 4)
    page(
        drv,
        f"{job}/configure",
        a / "task-07" / "jenkins-job-configuration.png",
        "#main-panel",
        4,
        max_height=4000,
    )
    page(
        drv, f"{job}/build?delay=0sec", a / "task-08" / "jenkins-build-with-parameters.png", "#main-panel", 2
    )
    page(drv, f"{job}/11/", a / "task-07" / "jenkins-build-11-summary.png", "#main-panel", 2)
    page(drv, f"{job}/11/testReport/", a / "task-07" / "jenkins-build-11-tests.png", "#main-panel", 2)
    page(drv, f"{job}/11/artifact/", a / "task-07" / "jenkins-build-11-artifacts.png", "#main-panel", 2)
    page(
        drv,
        f"{job}/11/artifact/reports/deployment.txt",
        a / "task-12" / "jenkins-build-11-deployment-record.png",
    )
    page(drv, f"{job}/2/", a / "task-10" / "jenkins-build-02-failed.png", "#main-panel", 2)
    page(drv, f"{job}/2/testReport/", a / "task-10" / "jenkins-build-02-failed-test.png", "#main-panel", 2)
    page(
        drv,
        f"{job}/9/testReport/",
        a / "task-10" / "jenkins-build-09-tests-no-stale-report.png",
        "#main-panel",
        2,
    )
    page(drv, f"{job}/3/", a / "task-10" / "jenkins-build-03-fixed.png", "#main-panel", 2)
    page(
        drv, f"{base}/manage/credentials/", a / "task-08" / "jenkins-credentials-masked.png", "#main-panel", 2
    )


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--jenkins-password")
    p.add_argument("--only", choices=["terminal", "browser"])
    p.add_argument("--rerender", action="store_true",
                   help="rebuild terminal images from the saved .txt files without re-running commands")
    args = p.parse_args()
    global RERENDER
    RERENDER = args.rerender
    drv = browser()
    try:
        if args.only != "browser":
            terminal(drv)
        if args.only != "terminal":
            browser_shots(drv, args.jenkins_password)
    finally:
        drv.quit()


if __name__ == "__main__":
    main()
