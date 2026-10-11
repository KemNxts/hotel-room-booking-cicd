# 1. Problem Definition and Scope (Task 1)

## Problem statement

A small hotel ("Grand Stay Hotel", 6 rooms) takes bookings by phone and
e-mail and records them in a spreadsheet. Guests cannot see which rooms are
free, staff re-type every request, and two people sometimes get the same
room for the same night. The hotel wants a simple **web booking portal**.

The **DevOps problem** is just as important as the app: changes must reach
guests quickly **without breaking bookings**. Manual copying of files to a
server, testing by hand "when there is time", and no way back after a bad
release are what this project replaces with an automated, tested,
repeatable **CI/CD pipeline**.

## Target users

| User | Needs |
|---|---|
| Guest | Register, log in, see free rooms for dates, request, confirm, cancel and track bookings |
| Developer (student team) | Fast feedback on every change; a safe way to release |
| Operator / examiner | Repeatable deployment, health checks, rollback |

## Stakeholders

| Stakeholder | Interest |
|---|---|
| Hotel owner | No double bookings, fewer phone calls |
| Front-desk staff | Accurate booking list and statuses |
| Guests | Self-service booking, clear status |
| Development team | Clean code structure, automated tests |
| Operations | Reliable deploys, health checks, rollback |
| Course instructor | All 15 tasks demonstrated with evidence |

## Existing pain points

1. Double bookings caused by manual tracking.
2. Guests cannot check availability themselves.
3. No status tracking: guests phone to ask "is my booking confirmed?".
4. Manual deployment: copy files, restart, hope.
5. No automated tests, so bugs are found by guests.
6. No rollback: a bad release stays until someone fixes it by hand.

## Objectives

| # | Objective |
|---|---|
| O1 | Deliver the six MVP booking workflows (below) |
| O2 | Guarantee no overlapping active bookings for a room - in code AND in the database |
| O3 | Automate build -> static checks -> tests -> package -> deploy in Jenkins |
| O4 | Block deployment automatically when any test fails (quality gate) |
| O5 | Package the app as Docker images tagged with version + commit |
| O6 | Provision a server and deploy with Ansible, idempotently |
| O7 | Recover from a bad release by rolling back to a tested earlier version |

## Constraints

**Technical**

- Python 3.11 + Flask + SQLite (team skills; no Java rewrite - see the
  "build tool" note in [03-srs-architecture.md](03-srs-architecture.md)).
- SQLite allows one writer at a time: fine for one hotel, not for many servers.
- Development machine is Windows 11; Jenkins, Docker and Ansible run in
  Linux containers (Docker Desktop).
- No public server: GitHub webhooks cannot reach the local Jenkins, so it polls.

**Operational**

- 10-day schedule, student team.
- No paid cloud services; local Docker registry instead of Docker Hub
  (Docker Hub is supported by setting a parameter + credential).
- Antivirus HTTPS scanning on the dev machine breaks downloads inside
  containers; handled by the optional `certs/` folder.

## Measurable success criteria

| Criterion | Target | Achieved (evidence) |
|---|---|---|
| MVP workflows working | 6 of 6 | 6 of 6 - Selenium journeys + integration tests ([06-test-plan.md](06-test-plan.md)) |
| Automated tests | >= 50, all passing | 90 passing (59 unit, 26 integration, 5 Selenium) |
| Double booking | impossible, even under concurrency | 10-thread race test + DB trigger tests pass |
| Pipeline duration | < 5 min | ~1 min (Jenkins builds #1-#8) |
| Failed test blocks deploy | always | Builds #2 and #9: deploy skipped, staging unchanged |
| Every deploy traceable | version + commit visible | `/health` and page footer, e.g. `1.1.0` / `d07929b` |
| Ansible re-run | `changed=0` | `docs/evidence/ansible/run3-repeat-idempotent.txt` |
| Rollback | no rebuild, verified working | Ansible `rollback.yml` switches to the stored older image; 5/5 Selenium journeys pass on the restored release |

## Approved MVP scope

In scope - the six booking workflows:

1. Registration and login
2. Room availability by date
3. Booking request (creates a PENDING booking)
4. Booking confirmation (PENDING -> CONFIRMED)
5. Booking cancellation (PENDING/CONFIRMED -> CANCELLED)
6. Booking status tracking ("My bookings")

...delivered through the 15 course tasks (planning, Git workflow, Jenkins,
Selenium, Docker, Ansible, release). See [15-task-checklist.md](15-task-checklist.md).

**Out of scope** (deliberately): payments, admin/staff UI, e-mail
notifications, room photos, multiple hotels, automatic expiry of PENDING
bookings, Kubernetes/cloud.
