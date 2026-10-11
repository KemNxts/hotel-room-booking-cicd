# Deliverable Checklist - All 15 Tasks

Legend: **Verified** = executed here and evidence saved; **Prepared** =
written/implemented but needs an action only you can do (e.g. GitHub account).

## Gap analysis at the start of this round (audit, 2026-10-11)

Baseline: 54 tests passing; all 6 MVP workflows working; Dockerfile,
compose, Jenkinsfile, Ansible playbook present. Docker image builds blocked
by antivirus HTTPS scanning.

| Task | State found | Missing work | Plan / verification |
|---|---|---|---|
| 1 Problem & scope | Only a README summary | Problem statement, users, stakeholders, objectives, criteria | Write doc 01 |
| 2 Agile | Nothing | Stories, AC, backlog, board, sprints, DoD, lifecycle | Write doc 02, link stories to tests |
| 3 SRS & architecture | README diagram | SRS, use cases, ER, routes; CSRF missing; overlap guard only in code | CSRF + DB triggers + integration tests; doc 03 |
| 4 Git init | Done | Branch policy OK | Keep; extend PR template |
| 5 Feature branch + PR | Branches merged locally | PR records | Prepared PR texts |
| 6 MVP + collaboration | MVP done | Merge conflict, tag, release | Two parallel footer features -> real conflict; v1.0.0, v1.1.0 |
| 7 Jenkins CI job | Jenkinsfile; never fully green (antivirus) | Lint, artifact, verified run | flake8, git-archive artifact, `certs/` fix, real runs |
| 8 Pipeline + deploy | Deploy stage existed | Version checks, deployment record | Health check compares version+commit |
| 9 Selenium | 5 journeys | - | Keep; evidence |
| 10 Continuous testing | Gate existed | Defect experiment, corrective commit, rerun | experiment branch, builds #2/#3 |
| 11 Docker lifecycle | Doc existed | Genuine evidence | Scripted lifecycle demo |
| 12 Jenkins-Docker CD | Images tagged with build no. | Commit SHA tag, registry push | `<version>-<sha>`, local registry |
| 13 Ansible | Playbook existed | Version-aware deploy, lab in repo | Lab compose; version assert |
| 14 Idempotency & rollback | Idempotency shown once | Rollback | `rollback.yml`, verified with Selenium |
| 15 Release & docs | README + viva notes | Report, guides, checklist, evidence | Docs 01-08, evidence folder |

## Final state

| # | Deliverable | Where | Status | Evidence |
|---|---|---|---|---|
| 1 | Problem, users, stakeholders, pain points, objectives, constraints, success criteria, scope | `docs/01-problem-definition.md` | Done | - |
| 2 | User stories + AC, backlog, Kanban, sprint plan, DoD, lifecycle diagram | `docs/02-agile-plan.md` | Done | Stories mapped to test names |
| 2 | Backlog linked to GitHub issues | - | **Prepared** | Needs push to GitHub, then create issues HB-01..15 |
| 3 | SRS, use-case, architecture, ER, data model, routes, setup, tech rationale | `docs/03-srs-architecture.md` | Done | - |
| 3 | 6 workflows + booking rules (dates, overlap, ownership, states, concurrency) | `app/`, `app/schema.sql` | **Verified** | 90 tests: `evidence/tests/local-run.txt` |
| 4 | README, .gitignore, .gitattributes, structure, templates, branch policy, baseline | repo root, `.github/`, `CONTRIBUTING.md` | Done | commit `08702db` |
| 5 | Feature branch, commits, tests, merge into develop | `feature/*` branches | **Verified** | `git log --graph`; `docs/04-git-workflow.md` |
| 5 | Pull request + review | `docs/pull-requests/` | **Prepared** | Real GitHub PRs need a push |
| 6 | All 6 workflows | app | **Verified** | Selenium 5/5, screenshots `app-*.png` |
| 6 | Second feature branch + real merge conflict + resolution | `feature/contact-footer`, `feature/release-footer` | **Verified** | `evidence/git/merge-conflict.txt`, merge `8728b62` |
| 6 | Version tags, release baseline | tags `v1.0.0`, `v1.1.0` on `main` | **Verified** | `git tag -n1` |
| 6 | Password hashing, sessions, validation, authorization, no secrets | app | **Verified** | integration tests (CSRF, cookies, 404 for others) |
| 7 | Jenkins job: checkout, Python env, deps, lint, pytest, reports, artifacts | `Jenkinsfile`, `deploy/jenkins/` | **Verified** | builds #1-#9, `evidence/jenkins/`, `jenkins-01-*.png` |
| 7 | Trigger | pollSCM (documented) | **Verified** (manual + API triggers used) | Webhook impossible without public Jenkins - documented |
| 8 | Pipeline as code with all stages, parameter, secrets outside Git, deploy, health check | `Jenkinsfile` | **Verified** | `build-01-green-staging.log`, `build-05-release-v1.0.0-prod.log` |
| 9 | 5 Selenium journeys, stable ids, explicit waits, isolated data, screenshots on failure | `tests/e2e/` | **Verified** | `evidence/tests/`, Jenkins Tests page |
| 10 | Tests in Jenkins, reports, failure propagation, quality gate | `Jenkinsfile` | **Verified** | build #2/#9 logs: "skipped due to earlier failure(s)" |
| 10 | Deliberate defect -> failure -> corrective commit -> green rerun | `experiment/defect-demo` (554cad3 -> 30c6a05) | **Verified** | builds #2 (fail), #3 (pass) |
| 11 | Dockerfile (slim base, pinned deps, Gunicorn, non-root, env config, no secrets, HEALTHCHECK), .dockerignore | `Dockerfile`, `.dockerignore`, `deploy/nginx/` | **Verified** | `evidence/docker/lifecycle.txt` |
| 11 | Build, tag, run, port mapping, logs, inspect, stop/restart/remove, persistent data | - | **Verified** | `evidence/docker/lifecycle.txt` |
| 12 | Build after tests, tag version + SHA, publish, deploy tested version, health check, record | `Jenkinsfile` | **Verified** (local registry) | registry tags list, `deployment.txt` artifact |
| 12 | Docker Hub publishing | `REGISTRY` param + `registry-creds` | **Prepared** | Needs a Docker Hub account/token |
| 13 | Inventory, playbook, variables, packages, dirs, config, permissions, ports, Nginx, health | `deploy/ansible/` | **Verified** (lab container) | `evidence/ansible/run1-*.txt` |
| 14 | First run, idempotent second run, health checks | - | **Verified** | `run1`, `run3` (`changed=0`) |
| 14 | Rollback + restored release works | `deploy/ansible/rollback.yml` | **Verified** | `run4-rollback.txt`, `run5-e2e-after-rollback.txt` (5/5) |
| 15 | End-to-end release (commit -> Jenkins -> tests -> gate -> image -> deploy -> health -> Ansible -> rollback) | all | **Verified** | docs 05, 07; builds #4-#8 |
| 15 | README, report, diagrams, SRS, guides, test plan, Docker/Ansible docs, troubleshooting, limitations, future work | `README.md`, `docs/` | Done | - |
| 15 | Screenshots + demo checklist | `docs/evidence/screenshots/`, report section 8 | Done (screenshots genuine) | Demo **video** still to be recorded by you |
| 15 | Viva questions and answers | `docs/viva-notes.md` | Done | - |

## Needs confirmation from the professor

- Whether Maven/Gradle/Ant and Tomcat are **mandatory** or examples (this
  Python project uses pip/pytest and Gunicorn + Nginx; see doc 03).

## What only you can do

1. Push to GitHub (`docs/04-git-workflow.md` has the commands), then create
   issues HB-01..HB-15 and, if required, open the prepared PRs.
2. Optional: Docker Hub account + `registry-creds` credential.
3. Optional: run the Ansible playbook against a real Ubuntu VM.
4. Record the demo video (checklist in `docs/08-project-report.md`).
