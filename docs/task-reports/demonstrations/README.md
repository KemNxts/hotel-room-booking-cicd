# Demonstration pack - all 15 tasks

Videos, narration scripts, command sheets, viva questions and screenshots for the 15 tasks of the
**CI/CD pipeline for a Hotel Room Booking Portal**. Everything here was produced by running the
real project; see [recording-capability-audit.md](recording-capability-audit.md) for how, and
[GENERATION_STATUS.md](GENERATION_STATUS.md) for what is finished, what is live and what must be done by you.

## The project in one paragraph

A small hotel (6 rooms) needs a web portal where guests register, see free rooms for their dates, request,
confirm and cancel bookings and track the status (Python + Flask + SQLite, layered controller / service / DAO).
The DevOps half makes every change safe: Git branches and tags, a Jenkins pipeline (lint, unit, integration and
Selenium tests as a quality gate), Docker images tagged with version and commit, a local registry, deployment
with Docker Compose, and Ansible to provision a server, re-run idempotently and roll back to an earlier release.

## How to use this pack

1. Watch the task's video once. The yellow text on screen is the narration; the same words are in `task-NN-narration.md`.
2. Repeat the commands from `task-NN-commands.md` yourself (they run in order, from the project folder).
3. Practise the answers in `task-NN-questions.md`.
4. If something is not running, the recovery table at the end of the command sheet tells you what to start.

## Master index

| # | Task | Video (path, length, audio) | Narration | Commands | Viva questions | Screenshots | Demonstration status | Remaining manual steps |
|---|---|---|---|---|---|---|---|---|
| 1 | Problem Definition and Scope | [task-01-demo.mp4](task-01/task-01-demo.mp4) - 3:49, voice-over (synthetic) + subtitles | [task-01-narration.md](task-01/task-01-narration.md) | [task-01-commands.md](task-01/task-01-commands.md) | [task-01-questions.md](task-01/task-01-questions.md) | [screenshots/](task-01/screenshots/) (8) | Demonstrated live and recorded | - |
| 2 | Agile Planning and DevOps Workflow | [task-02-demo.mp4](task-02/task-02-demo.mp4) - 4:56, voice-over (synthetic) + subtitles | [task-02-narration.md](task-02/task-02-narration.md) | [task-02-commands.md](task-02/task-02-commands.md) | [task-02-questions.md](task-02/task-02-questions.md) | [screenshots/](task-02/screenshots/) (11) | Demonstrated live and recorded | Create the GitHub issues (needs your login); the video states there are 0. |
| 3 | Requirements, Architecture and Technology Setup | [task-03-demo.mp4](task-03/task-03-demo.mp4) - 6:07, voice-over (synthetic) + subtitles | [task-03-narration.md](task-03/task-03-narration.md) | [task-03-commands.md](task-03/task-03-commands.md) | [task-03-questions.md](task-03/task-03-questions.md) | [screenshots/](task-03/screenshots/) (13) | Demonstrated live and recorded | Ask the professor whether Maven/Tomcat is mandatory. |
| 4 | Git and GitHub Repository Initialization | [task-04-demo.mp4](task-04/task-04-demo.mp4) - 5:25, voice-over (synthetic) + subtitles | [task-04-narration.md](task-04/task-04-narration.md) | [task-04-commands.md](task-04/task-04-commands.md) | [task-04-questions.md](task-04/task-04-questions.md) | [screenshots/](task-04/screenshots/) (12) | Demonstrated live and recorded | - |
| 5 | Feature Development with Branching | [task-05-demo.mp4](task-05/task-05-demo.mp4) - 4:48, voice-over (synthetic) + subtitles | [task-05-narration.md](task-05/task-05-narration.md) | [task-05-commands.md](task-05/task-05-commands.md) | [task-05-questions.md](task-05/task-05-questions.md) | [screenshots/](task-05/screenshots/) (11) | Real history shown + live practice repository | Open real pull requests on GitHub (needs your login). |
| 6 | MVP Completion and Git Collaboration | [task-06-demo.mp4](task-06/task-06-demo.mp4) - 7:59, voice-over (synthetic) + subtitles | [task-06-narration.md](task-06/task-06-narration.md) | [task-06-commands.md](task-06/task-06-commands.md) | [task-06-questions.md](task-06/task-06-questions.md) | [screenshots/](task-06/screenshots/) (19) | In progress | - |
| 7 | Jenkins Installation and Continuous Integration | NOT RECORDED | missing | missing | missing | none | not started | - |
| 8 | Pipeline as Code and Server Deployment | NOT RECORDED | missing | missing | missing | none | not started | - |
| 9 | Selenium Test Design and Local Execution | [task-09-demo.mp4](task-09/task-09-demo.mp4) - 7:37, voice-over (synthetic) + subtitles | [task-09-narration.md](task-09/task-09-narration.md) | [task-09-commands.md](task-09/task-09-commands.md) | [task-09-questions.md](task-09/task-09-questions.md) | [screenshots/](task-09/screenshots/) (16) | In progress | - |
| 10 | Continuous Testing in Jenkins | NOT RECORDED | missing | missing | missing | none | not started | - |
| 11 | Docker Image and Container Lifecycle | NOT RECORDED | missing | missing | missing | none | not started | - |
| 12 | Jenkins-Docker Continuous Deployment | NOT RECORDED | missing | missing | missing | none | not started | - |
| 13 | Configuration Management with Ansible | NOT RECORDED | missing | missing | missing | none | not started | - |
| 14 | Automated Provisioning and Reliability Validation (Idempotency and Rollback) | NOT RECORDED | missing | missing | missing | none | not started | - |
| 15 | Final End-to-End Release, Documentation and Viva | NOT RECORDED | missing | missing | missing | none | not started | - |

Other files: [recording-capability-audit.md](recording-capability-audit.md), [GENERATION_STATUS.md](GENERATION_STATUS.md), `_tools/` (the recorder and generators; re-run a recording with `_tools/record-demo.ps1 -TaskId NN`).
