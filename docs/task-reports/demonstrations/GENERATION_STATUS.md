# Generation status

Last updated: 2026-10-29

**Videos recorded and checked: 7 of 15.**

| # | Task | Video | Evidence type | Notes |
|---|---|---|---|---|
| 1 | Problem Definition and Scope | RECORDED 3:49 | live | Document walk-through plus a live run of the test suite (85 passed, 5 deselected). |
| 2 | Agile Planning and DevOps Workflow | RECORDED 4:56 | live | GitHub issue count read live from the GitHub API. |
| 3 | Requirements, Architecture and Technology Setup | RECORDED 6:07 | live | The real app was started and queried; code path traced. |
| 4 | Git and GitHub Repository Initialization | RECORDED 5:25 | live | Real repository state and a live GitHub API check. |
| 5 | Feature Development with Branching | RECORDED 4:48 | live | Practice add/commit/push/merge/pull ran in throw-away repos in TEMP, clearly labelled as practice. |
| 6 | MVP Completion and Git Collaboration | RECORDED 7:59 | live |  |
| 7 | Jenkins Installation and Continuous Integration | not recorded | - |  |
| 8 | Pipeline as Code and Server Deployment | not recorded | - |  |
| 9 | Selenium Test Design and Local Execution | RECORDED 7:37 | live |  |
| 10 | Continuous Testing in Jenkins | not recorded | - |  |
| 11 | Docker Image and Container Lifecycle | not recorded | - |  |
| 12 | Jenkins-Docker Continuous Deployment | not recorded | - |  |
| 13 | Configuration Management with Ansible | not recorded | - |  |
| 14 | Automated Provisioning and Reliability Validation (Idempotency and Rollback) | not recorded | - |  |
| 15 | Final End-to-End Release, Documentation and Viva | not recorded | - |  |

## Evidence type, in plain words

- **live**: the commands / browser actions in the video were executed for real while recording.
- **live + historical**: a live part, plus saved output from an earlier real run (the video says which).
- **historical**: the video displays genuine saved evidence (build logs, screenshots); nothing was re-run.

## What you must start yourself before showing the project

- Docker Desktop (it does not start by itself after a reboot) - needed for Tasks 7, 8, 10, 11, 12, 13, 14, 15.
- Jenkins and the local registry: `cd deploy\jenkins; docker compose up -d`, then wait about 1 minute for http://localhost:8090 (user `admin`, password in deploy/jenkins/.env - never show that file).
- For Tasks 13 and 14: `cd deploy\ansible\lab; docker compose up -d target`.
- Close other Chrome windows that automation could confuse, and do not touch the mouse during a recording.

## Things found while preparing this pack (not changed by me)

- docs/04-git-workflow.md ('Honest status of GitHub') and docs/pull-requests/README.md still say the repository was not pushed to GitHub. It was pushed on 2026-10-12 (public repo, 19 branches, tags v1.0.0 and v1.1.0 - confirmed live in the Task 4 video). Only issues and pull requests are missing.
- The same documents quote commit IDs from before the history rewrite (for example 8728b62, 37a4663). The current IDs differ; docs/evidence/git/commit-id-map.md maps old to new. The Task 5 and 6 videos use live Git queries instead.
- GitHub still has 0 issues and 0 pull requests (checked live). Creating them needs your GitHub login.
- Docker Hub publishing was never tested; only the local registry (localhost:5000) was used.
- The Ansible target is a privileged Docker container acting as a server, not a separate Ubuntu VM.
- The project is Python: Maven/Tomcat are not used. Whether Maven is mandatory is still a question for the professor.

## Environment state while recording

- Windows 11 laptop, ffmpeg 9.0.2 window capture, Windows text-to-speech voice (David) for the voice-over.
- Docker Desktop was stopped at the start of the session and was started by me; Jenkins, registry, staging and prod containers were stopped (exited 7 days ago).
- Working tree at the start: branch feature/ui-redesign, clean; the demonstrations folder is new and untracked. Nothing was committed or pushed.

## How to resume

Re-run a task: `powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId NN [-Part name]`,
then `.venv\Scripts\python docs/task-reports/demonstrations/_tools/join_parts.py NN` (multi-part tasks),
`build_support_files.py NN` and finally `build_index.py` to refresh this file and the README.
