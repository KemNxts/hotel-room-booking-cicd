# Hotel Room Booking Portal - CI/CD Project

A small hotel room booking web app used to demonstrate a complete CI/CD
pipeline: source control, automated tests, containerisation, a Jenkins
pipeline with a quality gate, a container registry, Ansible provisioning
and rollback. Current release: see [`VERSION`](VERSION) (tags `v1.0.0`, `v1.1.0`).

**Project documentation:** start at [docs/08-project-report.md](docs/08-project-report.md)
(report + index of all documents) and [docs/15-task-checklist.md](docs/15-task-checklist.md)
(all 15 course tasks mapped to files and evidence).

## Features (MVP)

1. User registration and login
2. Room availability view for a chosen date range
3. Booking request
4. Booking confirmation
5. Cancellation
6. Booking status tracking (`PENDING` -> `CONFIRMED` / `CANCELLED`)

## Tech stack

| Concern            | Tool                                  |
|--------------------|---------------------------------------|
| Language           | Python 3.11                           |
| Web framework      | Flask + Jinja2 templates              |
| Database           | SQLite (built into Python)            |
| Dependencies       | pip + pinned `requirements*.txt` + venv |
| Static checks      | `compileall` + flake8                 |
| Unit / integration tests | pytest (+ Flask test client)    |
| UI tests           | Selenium WebDriver (run via pytest)   |
| App server         | Gunicorn behind Nginx                 |
| Container          | Docker, Docker Compose                |
| Registry           | `registry:2` (local) or Docker Hub    |
| CI/CD              | Jenkins (declarative `Jenkinsfile`)   |
| Provisioning       | Ansible                               |

Why no Maven/Tomcat: they are Java tools; the Python equivalents are listed
in [docs/03-srs-architecture.md](docs/03-srs-architecture.md#note-on-maven--gradle--ant-and-tomcat).

## Repository layout

```
.
├── app/
│   ├── __init__.py         # create_app() factory, CSRF hook, /health endpoint
│   ├── config.py           # settings read from environment variables
│   ├── db.py               # SQLite connection per request, schema init, transactions
│   ├── schema.sql          # tables, constraints, overlap triggers, demo rooms
│   ├── models.py           # User, Room, Booking data classes, BookingStatus
│   ├── dao/                # Data Access Objects - the only place with SQL
│   ├── services/           # business rules (validation, availability, status changes)
│   ├── controllers/        # Flask routes + csrf.py
│   ├── templates/          # Jinja2 HTML pages
│   └── static/style.css
├── wsgi.py                 # entry point for Gunicorn / dev server
├── gunicorn.conf.py        # Gunicorn settings (workers, bind, logs)
├── VERSION                 # release number, baked into images and /health
├── requirements.txt        # runtime deps      requirements-dev.txt: + test/lint tools
├── pytest.ini, .flake8
├── tests/
│   ├── unit/               # service layer + database rules
│   ├── integration/        # HTTP routes via Flask test client
│   └── e2e/                # Selenium user journeys (screenshot on failure)
├── Dockerfile              # app image (Gunicorn, non-root, HEALTHCHECK, version labels)
├── docker-compose.yml      # nginx + app + database volume
├── .env.example            # template for the git-ignored .env
├── certs/                  # optional extra CA certificates (see certs/README.md)
├── Jenkinsfile             # CI/CD pipeline
├── deploy/
│   ├── nginx/              # reverse-proxy image + config
│   ├── jenkins/            # ready-to-run local Jenkins + registry
│   └── ansible/            # inventory, playbook, rollback, group_vars, controller image, lab/
├── scripts/capture_screenshots.py   # real screenshots of the running system
├── docs/                   # project documentation + evidence/
├── .github/                # issue + PR templates
├── CONTRIBUTING.md         # branching + commit message rules
└── README.md
```

## Branching

`feature/*` -> `develop` -> `main` (tagged releases). See
[CONTRIBUTING.md](CONTRIBUTING.md) and [docs/04-git-workflow.md](docs/04-git-workflow.md).

## Architecture

```
Browser ──> Nginx ──> Gunicorn ──> Controller (Flask route) ──> Service (rules) ──> DAO (SQL) ──> SQLite
                                         │                          │
                                         └── renders template       └── raises BookingError/AuthError
```

Each layer only talks to the one below it. Swapping SQLite for PostgreSQL would
change only the DAO layer; the services can be unit-tested without a browser.
Diagrams (use cases, ER, state machine): [docs/03-srs-architecture.md](docs/03-srs-architecture.md).

Booking lifecycle:

```
 request ──> PENDING ──confirm──> CONFIRMED
                │                     │
                └──────cancel─────────┴──> CANCELLED
```

A room is unavailable for a date range if it has a `PENDING` or `CONFIRMED`
booking that overlaps it. Check-out day = next guest's check-in day is allowed.
The rule is enforced by the service, a locking transaction, and a database trigger.

## Getting started (local development)

Requires Python 3.11+ (3.13 also works).

```bash
# 1. create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# Linux/macOS:           source .venv/bin/activate

# 2. install dependencies (incl. test tools)
pip install -r requirements-dev.txt

# 3. run the development server
python wsgi.py
```

Open http://127.0.0.1:5000. The database file is created automatically at
`instance/hotel.db` with six demo rooms. Delete that file to reset all data.

Health check: http://127.0.0.1:5000/health ->
`{"commit": "unknown", "env": "dev", "status": "ok", "version": "dev"}`

Production-style run (Linux/macOS/Docker only - Gunicorn does not run on Windows):

```bash
APP_ENV=prod SECRET_KEY=<long-random-string> gunicorn --config gunicorn.conf.py wsgi:app
```

## Running the tests

```bash
flake8 app tests scripts wsgi.py gunicorn.conf.py   # static checks
pytest -m "not e2e"     # unit + integration tests - fast, no browser needed
pytest -m e2e           # Selenium journeys - needs Google Chrome installed
pytest                  # everything (90 tests)
```

- **Unit tests** (`tests/unit/`, 59) test the service layer and database rules.
  Each test gets a fresh temporary SQLite file and "today" is frozen at
  2030-01-01, so results never depend on when the tests run.
- **Integration tests** (`tests/integration/`, 26) call the real routes:
  redirects, CSRF, cookies, access control, the whole booking lifecycle.
- **E2E tests** (`tests/e2e/`, 5) start the app on a free port and drive headless
  Chrome through 5 journeys: register, login (wrong + right password),
  search -> book -> confirm, cancel -> status tracking, and a booked room being
  unavailable to a second guest.
  - Watch the browser: `HEADLESS=0 pytest -m e2e` (PowerShell: `$env:HEADLESS="0"; pytest -m e2e`)
  - Test a running deployment instead: `E2E_BASE_URL=http://localhost:8080 pytest -m e2e`
  - On failure, a screenshot and the page HTML are saved in `reports/screenshots/`.

Test plan: [docs/06-test-plan.md](docs/06-test-plan.md).

## Running with Docker (Nginx + Gunicorn)

```bash
cp .env.example .env          # Windows: copy .env.example .env  - then set SECRET_KEY
docker compose up -d --build
```

Open http://localhost:8080. Requests go browser -> Nginx (port 8080) ->
Gunicorn (app container, port 8000, not published) -> SQLite in the
`hotel-data` volume. Images are tagged with `IMAGE_TAG` from `.env`, so you
can roll back with `IMAGE_TAG=<older> docker compose up -d --no-build`.
See [docs/container-lifecycle.md](docs/container-lifecycle.md) for all
build/run/stop/rollback commands.

> **Antivirus / proxy note:** products such as Avast/AVG "HTTPS scanning"
> intercept HTTPS with their own certificate, which Linux containers do not
> trust, so `pip install` inside `docker build` fails with
> `CERTIFICATE_VERIFY_FAILED`. Either turn off HTTPS scanning, or put that
> root certificate into `certs/` - see [certs/README.md](certs/README.md).

## CI/CD with Jenkins

`Jenkinsfile` stages: **Checkout -> Install dependencies -> Static checks
(flake8) -> Unit & integration tests -> E2E tests (Selenium) -> Package
source** (`git archive` + sha256) **-> Build images -> Publish images**
(registry) **-> Deploy** (compose pull + up --wait) **-> Health check**
(version and commit must match). A failing check fails its stage and skips
everything after it, so nothing broken is packaged or deployed. Test results
(JUnit XML), failure screenshots, the source archive and a deployment record
are attached to each build. Images are tagged `<VERSION>-<commit>`.

Parameters: `APP_ENV` (`staging` port 8081 | `prod` port 8082, separate
containers and data), `BRANCH` (which branch to build), `REGISTRY`
(`localhost:5000` or `docker.io/<you>` with a `registry-creds` credential).

### Run Jenkins locally (one command)

```bash
cd deploy/jenkins
cp .env.example .env          # Windows: copy .env.example .env  - set both values
docker compose up -d --build
```

Open http://localhost:8090, log in as `admin`. The job **hotel-booking** is
already created. Click **Build with Parameters** (default branch `develop`).
Jenkins only sees **committed** code. It also polls for new commits every ~5
minutes. The local registry runs at `localhost:5000`
(http://localhost:5000/v2/_catalog).

After a successful build: staging at http://localhost:8081, prod at http://localhost:8082.

Details, build history and the deliberate-defect experiment:
[docs/05-ci-cd-pipeline.md](docs/05-ci-cd-pipeline.md).

Using your own Jenkins instead: install plugins *Pipeline, Git, JUnit,
Credentials Binding*, add a *Secret text* credential with ID
`hotel-secret-key`, create a *Pipeline from SCM* job pointing at this repo
(branch `*/${BRANCH}`, lightweight checkout off), and make sure the agent has
`python3.11`, Chrome/Chromium and Docker.

## Provisioning with Ansible

`deploy/ansible/playbook.yml` takes a fresh **Ubuntu 22.04/24.04** server to a
running site: installs Docker + compose plugin, copies the app, writes a
root-only `.env` (with a generated `SECRET_KEY`), builds images tagged with
the release (only if not built yet), starts the containers and checks that
`/health` reports the expected version. Re-running it changes nothing
(idempotent). `rollback.yml` returns to the previous release.

**Try it without a VM** (disposable lab server in Docker):

```powershell
cd deploy\ansible\lab
docker compose up -d --build target
docker compose run --rm controller ansible-playbook -i lab/inventory.ini playbook.yml
# -> http://localhost:8088 ; run it again: changed=0
docker compose run --rm controller ansible-playbook -i lab/inventory.ini rollback.yml
docker compose down -v
```

**Real server:**

1. Put your server's IP and user in `deploy/ansible/inventory.ini`.
2. Run Ansible (Linux/macOS/WSL with Ansible installed):
   ```bash
   cd deploy/ansible
   ansible-playbook playbook.yml --ask-pass --ask-become-pass
   ```
   From Windows without WSL, use the provided controller image (from the repo root):
   ```powershell
   docker build -t hotel-ansible -f deploy/ansible/Dockerfile .
   docker run --rm -it -v "${PWD}:/work" hotel-ansible ansible-playbook playbook.yml --ask-pass --ask-become-pass
   ```
3. Open `http://<server-ip>/`.

Dry run: add `--check`. The generated key is stored on your machine in
`deploy/ansible/credentials/secret_key` (git-ignored). Details and evidence:
[docs/07-ansible.md](docs/07-ansible.md).

### Configuration (environment variables)

| Variable        | Default                  | Meaning                                   |
|-----------------|--------------------------|-------------------------------------------|
| `APP_ENV`       | `dev`                    | `dev`, `test`, `staging` or `prod`        |
| `SECRET_KEY`    | dev-only value           | Signs session cookies. **Required** outside dev/test |
| `DATABASE_PATH` | `instance/hotel.db`      | SQLite file location                      |
| `MAX_NIGHTS`    | `30`                     | Longest stay allowed per booking          |
| `APP_VERSION`, `GIT_COMMIT` | `dev`, `unknown` | Release info shown by `/health` (set at image build) |
| `SESSION_COOKIE_SECURE` | `0`              | `1` = session cookie only over HTTPS      |
| `IMAGE_TAG`, `IMAGE_PREFIX`, `HOST_PORT` | `latest`, empty, `8080` | Compose: which images, which registry, which port |

### Known limitations (deliberate, to keep the MVP small)

- PENDING bookings hold a room until confirmed or cancelled; there is no expiry.
- No admin screen; demo rooms come from `schema.sql`.
- No payment step; plain HTTP in the demo.
- SQLite = a single server. Full list: [docs/08-project-report.md](docs/08-project-report.md#6-known-limitations).
