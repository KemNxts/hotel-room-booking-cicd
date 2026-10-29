# Viva Cheat Sheet - CI/CD Pipeline for a Hotel Room Booking Portal

## 30-second introduction

"My project is a hotel room booking portal with a complete CI/CD pipeline.
Guests register, check availability, request, confirm and cancel bookings and
track their status. Every commit is checked by Jenkins with flake8 and 90
automated tests, including five Selenium browser journeys. Only if everything
passes are Docker images built, tagged with the version and commit, pushed to
a registry, deployed and health-checked. Ansible provisions a server the same
way every time, a second run changes nothing, and one command rolls back to
the previous release."

## 2-minute explanation

1. **Problem** - a small hotel books by phone and spreadsheet: double bookings, no self-service, risky manual releases.
2. **Application** - Python Flask with layers: controllers (HTTP), services (rules), DAOs (all SQL), SQLite. Six workflows. Passwords hashed, CSRF tokens, owner checks.
3. **Git** - `main` for releases, `develop` for integration, one `feature/*` branch per change, `--no-ff` merges, tags `v1.0.0` and `v1.1.0`, published on GitHub.
4. **Tests** - 59 unit, 26 integration, 5 Selenium; isolated temporary database; screenshots on failure.
5. **Jenkins** - the `Jenkinsfile` has 10 stages: checkout, install, static checks, unit & integration, Selenium, package source, build images, publish, deploy, health check. Parameter `APP_ENV` = staging (8081) or prod (8082). Secrets from Jenkins credentials.
6. **Docker** - slim Python image, non-root, volume for the database, HEALTHCHECK, Gunicorn behind Nginx; images tagged `<version>-<commit>` in a local registry.
7. **Ansible** - inventory, variables and a playbook that installs Docker, copies the app, writes a root-only `.env`, builds, starts and checks `/health`; idempotent; `rollback.yml`.
8. **Evidence** - Jenkins builds #1-#11, Ansible runs with `changed=7/5/0`, rollback verified by Selenium.

## The workflow in order

```
commit (feature branch) -> merge into develop -> Jenkins: checkout -> pip install (pinned)
-> flake8 -> pytest unit+integration -> Selenium -> [any failure: STOP, nothing deployed]
-> git archive + sha256 -> docker build (tag 1.1.0-<sha>) -> docker push (registry)
-> docker compose pull + up --wait -> /health must match version + commit -> deployment record
-> release: merge develop into main + tag vX.Y.Z -> deploy prod
-> Ansible: provision/deploy servers (idempotent) -> rollback.yml if needed
```

## Tools and their roles

| Tool | Role here |
|---|---|
| Git / GitHub | history, branches, tags / hosted copy (public) |
| Flask, SQLite | web app, database |
| pip + `requirements*.txt` | pinned dependencies (the Python equivalent of Maven's dependencies) |
| flake8, compileall | static checks |
| pytest | unit + integration tests, JUnit XML reports |
| Selenium WebDriver | browser journeys (headless Chrome) |
| Jenkins + `Jenkinsfile` | CI/CD pipeline as code |
| Docker, Docker Compose | images, containers, volume, health checks |
| `registry:2` | local image registry (Docker Hub supported, not used) |
| Gunicorn, Nginx | production WSGI server, reverse proxy (instead of Tomcat) |
| Ansible | configuration management, provisioning, rollback |

## The four implementation stories

**1. No double bookings (three layers).** The service checks availability;
the DAO checks and inserts inside `BEGIN IMMEDIATE` (a write-locked
transaction), so simultaneous requests queue; and SQLite triggers refuse any
overlapping active booking even if the code had a bug. Rule: existing
`check_in < new check_out AND check_out > new check_in`. A test fires 10
threads at once - exactly one booking is created.

**2. A failed quality gate prevented deployment.** On `experiment/defect-demo`
I changed `<` to `<=` in the overlap SQL (commit `5844eec`). Jenkins build #2
failed on `test_overlap_rules[2030-01-08-2030-01-10-True]`; Package, Build
images, Publish, Deploy and Health check were skipped; staging kept the old
version. The fix `2fb62d6` made build #3 green. Bonus: build #2's report also
showed 5 old Selenium results from a reused workspace - fixed with
`rm -rf reports dist`, proven by build #9.

**3. Merge conflict.** `feature/contact-footer` and `feature/release-footer`
both started at `da225fb` and added a footer in the same place. The second
merge conflicted in `base.html`, `style.css` and `test_routes.py`. I kept
both features, ran flake8 and all tests (89 passed) and committed merge
`9e766ac`. It can be replayed live in a throw-away clone.

**4. Rollback.** Every deploy tags images with the release and keeps old
ones; the playbook stores the previous release. `rollback.yml` switches
`IMAGE_TAG`, restarts with `--no-build` and asserts `/health`. On a fresh lab
server: v1.0.0 -> v1.1.0 -> repeat run `changed=0` -> rollback to 1.0.0 ->
v1.0.0's own Selenium journeys 5/5 passed.

## Common examiner questions

| Question | Short answer |
|---|---|
| CI vs CD? | CI = build + test every change; CD = also deploy automatically after tests pass |
| Git vs GitHub? | local history tool vs hosted service with issues/PRs |
| Branch vs tag? | moving pointer vs fixed label on one commit (releases) |
| Image vs container? | read-only package vs running instance |
| Registry vs Docker Hub? | any image store vs one hosted public registry; we use a local one |
| Playbook vs inventory? | what to do vs which servers |
| Idempotency vs repeatability? | no changes when already correct vs same end result each time |
| Unit vs integration vs Selenium? | one rule / real HTTP routes in-process / full browser journey |
| Build failure vs deployment failure? | stopped before deploy (users unaffected) vs new version unhealthy (rollback) |
| Deployment vs rollback? | forward to a new version vs back to an older tested image, no rebuild |
| What is a quality gate? | tests must pass before Deploy can run (stage order) |
| How is the secret handled? | Jenkins credential / Ansible-generated, `.env` 0600, `no_log`, never in Git |
| Why `/health`? | Docker, Jenkins and Ansible use it to check the app and its version/commit |
| Why Nginx + Gunicorn? | Gunicorn runs Python; Nginx is the public entry point and serves static files |

## Limitations - honest answers

| If asked | Answer |
|---|---|
| "Show me your GitHub issues / pull requests." | "There are none yet - GitHub shows 0. The backlog is in `docs/02-agile-plan.md`, merges were done locally with `--no-ff` and pushed, and review records are in `docs/pull-requests/`. Creating the issues and PRs is my next step." |
| "Did you publish to Docker Hub?" | "No. The pipeline supports it with a `registry-creds` credential and the REGISTRY parameter, but I tested only the local registry." |
| "Did you deploy to a real server?" | "Ansible was run against a disposable Ubuntu container with systemd and SSH, not a VM. The same playbook targets a real server by editing `inventory.ini`." |
| "Where is Maven / Tomcat?" | "It's a Python project: pip, flake8 and pytest do the dependency/compile/test jobs; Gunicorn + Nginx serve it. I need your confirmation that this equivalent is acceptable." |
| "Why polling and not a webhook?" | "Jenkins runs on localhost, which GitHub can't reach." |
| "Why do commit IDs differ between logs and GitHub?" | "Commit messages were edited once before publishing; the map is `docs/evidence/git/commit-id-map.md`." |
| "Is the new design deployed?" | "Not yet - the redesign is on `feature/ui-redesign`, uncommitted. Prod runs v1.1.0." |
| "Zero downtime?" | "No - rollback re-creates containers, a few seconds' interruption." |

## Commands for the practical (PowerShell, from `D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING`)

```powershell
# 0. before anything: start Docker Desktop, then
docker ps --format "table {{.Names}}\t{{.Status}}"

# app locally (port 5000 is used by the registry)
.venv\Scripts\python -m flask --app wsgi run --port 5001

# tests
.venv\Scripts\python -m flake8 -j 1 app tests scripts wsgi.py gunicorn.conf.py
.venv\Scripts\python -m pytest -q -m "not e2e"
$env:HEADLESS="0"; .venv\Scripts\python -m pytest -m e2e -v; Remove-Item Env:HEADLESS

# git
git log --graph --oneline -12 develop
git tag -n1
git show --stat 9e766ac

# deployed versions and registry
curl.exe -s http://localhost:8081/health
curl.exe -s http://localhost:8082/health
curl.exe -s http://localhost:5000/v2/hotel-booking-app/tags/list

# Jenkins (if not running)
cd deploy\jenkins; docker compose up -d; cd ..\..
#   -> http://localhost:8090, job hotel-booking, Build with Parameters

# Ansible lab
cd deploy\ansible\lab
docker compose up -d target
docker compose run --rm controller ansible-playbook -i lab/inventory.ini playbook.yml
docker compose run --rm controller ansible-playbook -i lab/inventory.ini playbook.yml -e app_version=1.1.1-demo
docker compose run --rm controller ansible-playbook -i lab/inventory.ini rollback.yml
curl.exe -s http://localhost:8088/health
```
