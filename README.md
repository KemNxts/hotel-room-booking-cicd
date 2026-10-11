# Hotel Room Booking Portal - CI/CD Project

A small hotel room booking web app used to demonstrate a complete CI/CD
pipeline: source control, automated tests, containerisation, a Jenkins
pipeline and Ansible provisioning.

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
| Dependencies       | pip + `requirements.txt` + venv       |
| Unit tests         | pytest                                |
| UI tests           | Selenium WebDriver (run via pytest)   |
| App server         | Gunicorn behind Nginx                 |
| Container          | Docker                                |
| CI/CD              | Jenkins (declarative `Jenkinsfile`)   |
| Provisioning       | Ansible                               |

## Repository layout

```
.
├── app/
│   ├── __init__.py         # create_app() factory + /health endpoint
│   ├── config.py           # settings read from environment variables
│   ├── db.py               # SQLite connection per request, schema init, transactions
│   ├── schema.sql          # tables + demo rooms
│   ├── models.py           # User, Room, Booking data classes, BookingStatus
│   ├── dao/                # Data Access Objects - the only place with SQL
│   ├── services/           # business rules (validation, availability, status changes)
│   ├── controllers/        # Flask routes: read request -> call service -> render
│   ├── templates/          # Jinja2 HTML pages
│   └── static/style.css
├── wsgi.py                 # entry point for Gunicorn / dev server
├── gunicorn.conf.py        # Gunicorn settings (workers, bind, logs)
├── requirements.txt        # runtime deps      requirements-dev.txt: + test tools
├── pytest.ini
├── tests/
│   ├── unit/               # pytest tests of the service layer
│   └── e2e/                # Selenium user journeys (screenshot on failure)
├── Dockerfile              # app image (Gunicorn, non-root, HEALTHCHECK)
├── docker-compose.yml      # nginx + app + database volume
├── .env.example            # template for the git-ignored .env
├── Jenkinsfile             # CI/CD pipeline
├── deploy/
│   ├── nginx/              # reverse-proxy image + config
│   ├── jenkins/            # ready-to-run local Jenkins (image, plugins, job setup)
│   └── ansible/            # inventory, playbook, group_vars, controller image
├── docs/
│   ├── container-lifecycle.md
│   └── viva-notes.md       # design decisions explained
├── .github/                # issue + PR templates
├── CONTRIBUTING.md         # branching + commit message rules
└── README.md
```

## Branching

`feature/*` -> `develop` -> `main`. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Architecture

```
Browser ──HTTP──> Controller (Flask route) ──> Service (rules) ──> DAO (SQL) ──> SQLite
                        │                          │
                        └── renders template       └── raises BookingError/AuthError
```

Each layer only talks to the one below it. Swapping SQLite for PostgreSQL would
change only the DAO layer; the services can be unit-tested without a browser.

Booking lifecycle:

```
 request ──> PENDING ──confirm──> CONFIRMED
                │                     │
                └──────cancel─────────┴──> CANCELLED
```

A room is unavailable for a date range if it has a `PENDING` or `CONFIRMED`
booking that overlaps it. Check-out day = next guest's check-in day is allowed.

## Getting started (local development)

Requires Python 3.11+.

```bash
# 1. create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# Linux/macOS:           source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. run the development server
python wsgi.py
```

Open http://127.0.0.1:5000. The database file is created automatically at
`instance/hotel.db` with six demo rooms. Delete that file to reset all data.

Health check: http://127.0.0.1:5000/health -> `{"env": "dev", "status": "ok"}`

Production-style run (Linux/macOS/Docker only - Gunicorn does not run on Windows):

```bash
APP_ENV=prod SECRET_KEY=<long-random-string> gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app
```

## Running the tests

```bash
pip install -r requirements-dev.txt

pytest -m "not e2e"     # unit tests only - fast, no browser needed
pytest -m e2e           # Selenium journeys - needs Google Chrome installed
pytest                  # everything
```

- **Unit tests** (`tests/unit/`) test the service layer directly. Each test
  gets a fresh temporary SQLite file and "today" is frozen at 2030-01-01, so
  results never depend on when the tests run.
- **E2E tests** (`tests/e2e/`) start the app on a free port and drive headless
  Chrome through 5 journeys: register, login (wrong + right password),
  search -> book -> confirm, cancel -> status tracking, and a booked room being
  unavailable to a second guest.
  - Watch the browser: `HEADLESS=0 pytest -m e2e` (PowerShell: `$env:HEADLESS="0"; pytest -m e2e`)
  - Test a running deployment instead: `E2E_BASE_URL=http://localhost:8080 pytest -m e2e`
  - On failure, a screenshot and the page HTML are saved in `reports/screenshots/`.

## Running with Docker (Nginx + Gunicorn)

```bash
cp .env.example .env          # Windows: copy .env.example .env  - then set SECRET_KEY
docker compose up -d --build
```

Open http://localhost:8080. Requests go browser -> Nginx (port 8080) ->
Gunicorn (app container, port 8000, not published) -> SQLite in the
`hotel-data` volume. See [docs/container-lifecycle.md](docs/container-lifecycle.md)
for all build/run/stop commands.

> **Antivirus note (Avast/AVG/Kaspersky "HTTPS scanning"):** these products
> intercept HTTPS with their own certificate, which Linux containers do not
> trust, so `pip install` inside `docker build` fails with
> `CERTIFICATE_VERIFY_FAILED`. Turn off HTTPS scanning while building
> (Avast: Settings -> Protection -> Core Shields -> Web Shield ->
> untick "Enable HTTPS scanning").

## CI/CD with Jenkins

`Jenkinsfile` stages: **Checkout -> Build** (venv + pip) **-> Unit tests -> E2E
tests -> Package** (docker images tagged with the build number) **-> Deploy**
(docker compose + health check). A failing test fails its stage and stops the
pipeline, so nothing broken is packaged or deployed. Test results (JUnit XML)
and failure screenshots are attached to each build.

Parameter `APP_ENV` (`staging` | `prod`) chooses the environment: it sets
`APP_ENV` inside the container, the port (staging 8081, prod 8082) and a
separate compose project, so each environment has its own containers and data.

### Run Jenkins locally (one command)

```bash
cd deploy/jenkins
cp .env.example .env          # Windows: copy .env.example .env  - set both values
docker compose up -d --build
```

Open http://localhost:8090, log in as `admin`. The job **hotel-booking** is
already created. It builds the `develop` branch of this folder (commit first,
Jenkins only sees committed code). Click **Build Now**; the first run uses the
default `APP_ENV=staging`, later runs show **Build with Parameters**. Jenkins
also polls for new commits every ~5 minutes.

After a successful build: staging app at http://localhost:8081.

Using your own Jenkins instead: install plugins *Pipeline, Git, JUnit,
Credentials Binding*, add a *Secret text* credential with ID
`hotel-secret-key`, create a *Pipeline from SCM* job pointing at this repo,
and make sure the agent has `python3.11`, Chrome/Chromium and Docker.

## Provisioning with Ansible

`deploy/ansible/playbook.yml` takes a fresh **Ubuntu 22.04/24.04** server to a
running site: installs Docker + compose plugin, copies the app, writes a
root-only `.env` (with a generated `SECRET_KEY`), builds the images, starts
the containers and checks `/health` through Nginx. Re-running it changes
nothing unless something changed (idempotent).

1. Put your server's IP and user in `deploy/ansible/inventory.ini`.
2. Run Ansible (Linux/macOS/WSL with Ansible installed):
   ```bash
   cd deploy/ansible
   ansible-playbook playbook.yml --ask-pass --ask-become-pass
   ```
   From Windows without WSL, use the provided controller image (from the repo root):
   ```powershell
   docker build -t hotel-ansible deploy/ansible
   docker run --rm -it -v "${PWD}:/work" hotel-ansible ansible-playbook playbook.yml --ask-pass --ask-become-pass
   ```
3. Open `http://<server-ip>/`.

Dry run: add `--check`. The generated key is stored on your machine in
`deploy/ansible/credentials/secret_key` (git-ignored).

### Configuration (environment variables)

| Variable        | Default                  | Meaning                                   |
|-----------------|--------------------------|-------------------------------------------|
| `APP_ENV`       | `dev`                    | `dev`, `test`, `staging` or `prod`        |
| `SECRET_KEY`    | dev-only value           | Signs session cookies. **Required** outside dev/test |
| `DATABASE_PATH` | `instance/hotel.db`      | SQLite file location                      |
| `MAX_NIGHTS`    | `30`                     | Longest stay allowed per booking          |

### Known limitations (deliberate, to keep the MVP small)

- No CSRF tokens on forms (would add Flask-WTF in a real system).
- PENDING bookings hold a room until confirmed or cancelled; there is no expiry.
- No admin screen; demo rooms come from `schema.sql`.
- No payment step.
