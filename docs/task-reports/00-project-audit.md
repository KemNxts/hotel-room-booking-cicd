# 00 - Project Audit (before writing the task reports)

**Audit date:** 2026-10-20. **Auditor:** documentation pass over the real repository, services and evidence.
Every "verified" below means a command was run or a page was opened on this date and the result was seen.

## 1. Repository state

| Item | Actual value (2026-10-20) | How checked |
|---|---|---|
| Local path | `D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING` | - |
| Current branch | `feature/ui-redesign` | `git branch --show-current` |
| Uncommitted work | The UI redesign (templates, CSS, `app.js`, fonts, 4 test assertions, `scripts/capture_ui.py`, `docs/09-ui-design.md`, `docs/ui-evidence/`) **and** one edit by the student to `docs/01-problem-definition.md`. None of it is committed or pushed. | `git status --short` (see `assets/task-15/git-status-final.png`) |
| Latest commit on `develop` | `1c2103c` Merge branch 'docs/history-rewrite' into develop | `git log` |
| `main` | `bea6a4c` (docs merge after release `v1.1.0`) | `git log --first-parent main` |
| Tags | `v1.0.0` -> `224de14`, `v1.1.0` -> `ce1726d` (annotated) | `git tag -n1`, `git cat-file -p v1.1.0` |
| Local branches | 20: `main`, `develop`, 13 `feature/*` (including the unpushed `feature/ui-redesign`), 1 `fix/*`, 2 `experiment/*`, 2 `docs/*` | `git branch -a` |
| Remote | `origin` = https://github.com/KemNxts/hotel-room-booking-cicd (public) | `git remote -v`, GitHub API |

### Commit IDs changed once (important when reading evidence)

On 2026-10-12, before publishing to GitHub, commit messages were edited to
remove a co-author line. File contents did not change, but every commit ID
did. Evidence captured **before** that date (Jenkins logs of builds #1-#10,
`docs/evidence/`) shows the **original** IDs; Git and GitHub today show the
**current** IDs. The full mapping is in
[`docs/evidence/git/commit-id-map.md`](../evidence/git/commit-id-map.md).
The IDs used most often:

| Meaning | Original ID (old evidence) | Current ID (Git/GitHub now) |
|---|---|---|
| release v1.0.0 | `661751d` | `224de14` |
| release v1.1.0 | `d07929b` | `ce1726d` |
| deliberate defect | `554cad3` | `5844eec` |
| corrective commit | `30c6a05` | `2fb62d6` |
| merge-conflict resolution | `8728b62` | `9e766ac` |
| first commit (skeleton) | `08702db` | `541dad5` |

Note: the Docker images in the local registry and the running staging/prod
containers were built before the rewrite, so their tags and `/health` also
show original IDs (e.g. prod = `1.1.0-d07929b`). Jenkins build #11 (2026-10-20)
was built after the rewrite and shows the current ID `1c2103c`.

## 2. GitHub (checked through the public GitHub REST API, read-only)

| Item | Result |
|---|---|
| Repository | exists, public, default branch `main`, last push 2026-10-12 |
| Branches on GitHub | 19 (everything except `feature/ui-redesign`) |
| Tags on GitHub | `v1.0.0`, `v1.1.0` |
| Issues | **0** - not created yet |
| Pull requests | **0** - not created yet; merges were done locally with `git merge --no-ff` and pushed |

## 3. Fresh verification run on 2026-10-20

| Check | Command | Result | Evidence |
|---|---|---|---|
| Lint | `.venv\Scripts\flake8 -j 1 app tests scripts wsgi.py gunicorn.conf.py` | no findings | `assets/task-09/full-test-suite.png` |
| Unit tests | `.venv\Scripts\python -m pytest tests/unit` | **59 passed** | same |
| Integration tests | `... pytest tests/integration` | **26 passed** | same |
| Selenium tests | `... pytest tests/e2e` | **5 passed** | `assets/task-09/selenium-run.png` |
| Screenshot on failure | temporary failing test (deleted afterwards) | screenshot + HTML saved by the hook | `assets/task-09/selenium-failure-*.png` |
| Jenkins build #11 | Build with parameters `BRANCH=develop`, `APP_ENV=staging` | **SUCCESS**, all 10 stages, 90 tests, images `1.1.0-1c2103c` pushed and deployed, health check passed | `assets/raw/jenkins-build-11.log`, `assets/task-07/*`, `assets/task-08/*` |
| Jenkins history | Jenkins REST API | builds #1-#11 present; #2 and #9 FAILURE (deliberate), all others SUCCESS | `assets/task-07/jenkins-job-stage-view.png` |
| Docker lifecycle | scripted demo (build, tag, run, ports, logs, inspect, stop/start/restart, rm, new container on same volume) | all steps worked; an account created in the first container could log in from the second | `assets/raw/docker-lifecycle.txt`, `assets/task-11/lifecycle-*.png` |
| Local registry | `GET localhost:5000/v2/hotel-booking-app/tags/list` | 8 tags incl. `1.1.0-1c2103c` | `assets/task-12/registry-tags.png` |
| Ansible, fresh lab server | runs from clean clones of tags v1.0.0 and v1.1.0 | run 1 `changed=7`, run 2 `changed=5`, run 3 **`changed=0`**, rollback `changed=3` -> 1.0.0 | `assets/raw/ansible-run1..4*.txt` |
| Restored release works | v1.0.0's own Selenium tests against the rolled-back server | **5 passed** | `assets/raw/ansible-run5-e2e-after-rollback.txt` |
| Demo commands in the reports | Docker demo (Task 11), Ansible lab demo incl. rollback (Tasks 13/14), merge-conflict replay in a throw-away clone (Task 6) | all ran as written | (outputs checked during the audit) |
| Running services | `/health` of each | dev `:5001` ok, staging `:8081` ok (`1c2103c`), prod `:8082` ok (`d07929b`), lab `:8088` ok, Jenkins `:8090` up, registry `:5000` up | `assets/task-15/all-environments-health.png` |

## 4. Status of the 15 tasks

| # | Task | Status | Reason |
|---|---|---|---|
| 1 | Problem definition and scope | Implemented and verified | Document exists and is published on GitHub |
| 2 | Agile planning and DevOps workflow | **Partially completed** | Backlog, stories, board, DoD, diagram exist; **GitHub issues = 0 (pending external action)** |
| 3 | Requirements, architecture and setup | Implemented and verified | Routes, layers and tests checked today |
| 4 | Git and GitHub initialization | Implemented and verified | Repo, templates, branches, tags on GitHub (API) |
| 5 | Feature development with branching | **Partially completed** | Feature branches + `--no-ff` merges verified; **real GitHub PRs = 0 (pending external action)** |
| 6 | MVP completion and collaboration | Implemented and verified | 6 features pass tests today; conflict reproduced today in a clone; tags exist |
| 7 | Jenkins installation and CI | Implemented and verified | Build #11 today. Polling, not a webhook (no public URL). Maven not used - confirm with professor |
| 8 | Pipeline as code and deployment | Implemented and verified | Build #11 deployed staging and passed the health check |
| 9 | Selenium test design and execution | Implemented and verified | 5/5 today; failure screenshot hook shown today |
| 10 | Continuous testing in Jenkins | Implemented and verified | Builds #2/#3/#9 records checked today (experiment itself run 2026-10-11) |
| 11 | Docker image and container lifecycle | Implemented and verified | Full lifecycle re-run today |
| 12 | Jenkins-Docker continuous deployment | Implemented and verified (local registry) | **Docker Hub publishing not tested - pending external action** (needs an account) |
| 13 | Configuration management with Ansible | Implemented and verified (container lab) | Target is a privileged Docker container, **not a separate VM** |
| 14 | Provisioning, idempotency and rollback | Implemented and verified (container lab) | Re-run today: `changed=0`, rollback + 5/5 Selenium |
| 15 | End-to-end release and documentation | Implemented and verified, with pending external items | See the limitations below |

## 5. Limitations and pending actions (not hidden)

1. **GitHub issues** - none created. Backlog exists as `docs/02-agile-plan.md` (HB-01..HB-15).
2. **GitHub pull requests** - none created. PR texts prepared in `docs/pull-requests/`. Merges were real local merges, now visible on GitHub.
3. **Docker Hub** - publishing path is implemented (`REGISTRY` parameter + `registry-creds` credential) but never run; the local `registry:2` was used.
4. **Ansible target** - a disposable Ubuntu 24.04 container with systemd + SSH, not a separate VM or cloud server.
5. **Maven/Gradle/Ant and Tomcat** - not used. This is a Python project: pip + pytest + flake8 are used for build/test, Gunicorn + Nginx for serving. Whether this satisfies the brief **needs the professor's confirmation**.
6. **Webhook** - Jenkins polls Git every ~5 minutes; a GitHub webhook needs a publicly reachable Jenkins.
7. **UI redesign not committed** - application screenshots in Tasks 3, 6, 9 and 15 show the redesigned interface running from the working tree (dev server). The deployed staging/prod containers still run the v1.1.0 interface (see `assets/task-12/prod-portal-v1.1.0.png`). Commit it, merge it and run Jenkins to deploy it.
8. **Branch protection rules** on GitHub were not configured (documented as a policy in `CONTRIBUTING.md` only). Cannot be checked without logging in to GitHub.

## 6. Environment notes

- Windows 11, Docker Desktop 29.7.2, Python 3.13 venv (pipeline uses 3.11), Chrome for Selenium.
- Avast HTTPS scanning intercepts TLS; containers trust its root certificate through the optional `certs/` folder.
- Port 5000 is used by the local Docker registry, so the development server must use another port: `python -m flask --app wsgi run --port 5001`.
- Docker Desktop does not start automatically after a reboot.

## 7. About the screenshots in these reports

- Browser screenshots are real captures (headless Chrome) of the running portal, Jenkins, the registry and the public GitHub pages.
- "Terminal" images were produced by `scripts/capture_report_evidence.py`: the command was run for real, its raw output saved as `.txt` beside the image, and the output rendered as an image. Each such image says so in its footer. Images of older logs say which log file they were rendered from.
- No screenshot was edited. No GitHub PR, hosted registry or remote server is shown because none exists.
