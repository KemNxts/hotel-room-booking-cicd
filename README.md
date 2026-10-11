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
├── requirements.txt
├── tests/
│   ├── unit/               # pytest unit tests (Phase 3)
│   └── e2e/                # Selenium user-journey tests (Phase 3)
├── deploy/
│   └── ansible/            # inventory + playbook (Phase 6)
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

### Configuration (environment variables)

| Variable        | Default                  | Meaning                                   |
|-----------------|--------------------------|-------------------------------------------|
| `APP_ENV`       | `dev`                    | `dev`, `test` or `prod`                   |
| `SECRET_KEY`    | dev-only value           | Signs session cookies. **Required** in prod |
| `DATABASE_PATH` | `instance/hotel.db`      | SQLite file location                      |
| `MAX_NIGHTS`    | `30`                     | Longest stay allowed per booking          |

### Known limitations (deliberate, to keep the MVP small)

- No CSRF tokens on forms (would add Flask-WTF in a real system).
- PENDING bookings hold a room until confirmed or cancelled; there is no expiry.
- No admin screen; demo rooms come from `schema.sql`.
- No payment step.
