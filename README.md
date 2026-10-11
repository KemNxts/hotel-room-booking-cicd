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
├── app/                    # Flask application (added in Phase 2)
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

## Getting started

Run instructions are added in Phase 2.
