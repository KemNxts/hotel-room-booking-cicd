# 6. Test Plan and Reports (Tasks 9, 10)

## Strategy - the test pyramid

| Level | Folder | Count | Speed | What it proves |
|---|---|---|---|---|
| Unit | `tests/unit/` | 59 | ~7 s | Business rules in services; database constraints and triggers |
| Integration | `tests/integration/` | 26 | ~4 s | Real HTTP routes through Flask's test client: redirects, status codes, sessions, CSRF, access control |
| End-to-end (Selenium) | `tests/e2e/` | 5 | ~25 s | Complete user journeys in a real (headless) Chrome |
| **Total** | | **90** | ~40 s | |

Plus **static checks**: `python -m compileall` and `flake8` (config: `.flake8`).

Many fast tests at the bottom, few slow browser tests at the top: failures
are found quickly and pinpointed precisely.

## Test isolation and deterministic data

- **Unit/integration:** every test gets a brand-new SQLite file in pytest's
  `tmp_path` - no shared state, any order, repeatable.
- **Frozen date:** booking unit tests use "today = 2030-01-01"
  (`FROZEN_TODAY`), so date rules give the same results every day.
- **Selenium:** the `base_url` fixture starts the real app on a free port
  with a **throw-away database** (deleted after the run). Against a running
  deployment (`E2E_BASE_URL=...`) the tests still work because they use
  unique e-mails (`uuid`) and random far-future dates, and book whichever
  room is free.

## Selenium journeys (Task 9)

| # | Journey | Steps | Assertions |
|---|---|---|---|
| 1 | Register a new guest | Open /register, fill form, submit | Name in navbar, "account has been created" message, redirected to /rooms |
| 2 | Wrong then right password | Register, log out, log in with wrong password, then correct one | "Invalid email or password", still logged out; then "Welcome back" |
| 3 | Search, request and confirm | Search dates, click Book on first free room, Confirm | Status PENDING with the right dates; then CONFIRMED, "Booking confirmed", no second Confirm button |
| 4 | Cancel and track status | Book, confirm, cancel, open My bookings | CANCELLED, no Cancel button; My bookings row shows CANCELLED |
| 5 | Booked room unavailable to others | Guest A books; guest B searches the same dates | Room shown "Booked" for B, no Book button |

Good practice used:

- **Stable selectors:** element ids added for testing (`register-btn`,
  `booking-status`, `room-101`, `book-101`, `booking-row-<id>` ...), never
  fragile XPath or CSS positions.
- **Explicit waits** (`WebDriverWait` + expected conditions), never `sleep`.
- **Date inputs** are set with JavaScript, because typing into
  `<input type="date">` depends on the OS locale (dd/mm vs mm/dd).
- **Screenshots on failure:** a pytest hook (`pytest_runtest_makereport` in
  `tests/e2e/conftest.py`) records the result; the `driver` fixture then saves
  `reports/screenshots/<test>.png` and the page HTML. Jenkins archives them.

## UI redesign and the tests

The 2026-10-20 redesign kept every form field, route and id the tests rely
on. Four assertions changed with the UI contract (rooms as cards, readable
dates in `<time datetime>`, a confirmation dialog before cancelling) - each
stays at least as strict; details in [09-ui-design.md](09-ui-design.md#test-contract-changes).
Visual checks: `python scripts/capture_ui.py` screenshots every page at 3
screen sizes and fails if any page overflows horizontally.

## Running the tests

```powershell
pytest                                   # everything (needs Chrome for e2e)
pytest -m "not e2e"                      # unit + integration only
pytest -m e2e                            # browser journeys
$env:HEADLESS="0"; pytest -m e2e         # watch the browser
$env:E2E_BASE_URL="http://localhost:8080"; pytest -m e2e   # test a running deployment
pytest --junitxml=reports/tests.xml      # JUnit XML report (what Jenkins reads)
```

Note on Maven: the brief mentions running Selenium through Maven. These are
**Python** tests; they run through **pytest**, which produces the same JUnit
XML format Maven's Surefire plugin would, and Jenkins' JUnit plugin displays
it. See the Maven note in [03-srs-architecture.md](03-srs-architecture.md).

## Critical business rules covered (selection)

| Rule | Tests |
|---|---|
| Invalid date ranges / past dates / > 30 nights | `TestValidateStay::test_invalid_stays_are_rejected` (parametrised), `test_past_dates_cannot_be_booked` |
| Overlap rules incl. back-to-back stays | `TestSearchRooms::test_overlap_rules` (parametrised) |
| Overlapping request refused | `test_overlapping_booking_is_rejected`, `test_overlapping_request_for_same_room_is_refused` |
| Different rooms, same dates allowed | `test_different_rooms_can_be_booked_for_the_same_dates` |
| Concurrency: 10 simultaneous requests -> 1 booking | `test_simultaneous_requests_create_only_one_booking` |
| Database refuses overlaps even without the service | `test_trigger_rejects_overlapping_insert`, `test_trigger_rejects_reactivating_...` |
| Invalid booking ids | `test_invalid_booking_ids_return_404`, `test_get_missing_booking_raises_not_found` |
| Unauthorised view/confirm/cancel | `test_other_users_cannot_see_confirm_or_cancel_my_booking`, `test_other_user_cannot_cancel` |
| Repeated cancellation | `test_cannot_cancel_twice`, `test_repeated_cancellation_is_refused` |
| Availability after booking and cancellation | `test_cancelled_booking_frees_the_room`, `test_cancelled_room_can_be_booked_again` |
| CSRF | `test_post_without_csrf_token_is_rejected`, `test_post_with_wrong_csrf_token_is_rejected` |
| Seeding safe on restart | `test_init_db_can_run_repeatedly_without_duplicating_rooms` |

## Reports (genuine)

| Report | Where |
|---|---|
| Local run: flake8 + 90 tests, verbose | [evidence/tests/local-run.txt](evidence/tests/local-run.txt) |
| JUnit XML of that run | [evidence/tests/junit-all.xml](evidence/tests/junit-all.xml) |
| Jenkins test results | Jenkins -> build -> *Tests*; screenshots `evidence/screenshots/jenkins-03-*.png`, `jenkins-05-*.png` |
| Selenium against the rolled-back server (5/5) | [evidence/ansible/run5-e2e-after-rollback.txt](evidence/ansible/run5-e2e-after-rollback.txt) |

## Do the tests really catch bugs?

Yes - checked by deliberately breaking code:

- `<` -> `<=` in the overlap SQL: `test_overlap_rules[...-True]` fails
  (Jenkins build #2 and #9, see [05-ci-cd-pipeline.md](05-ci-cd-pipeline.md)).
- (Earlier, before the database trigger existed) removing the locking
  transaction made the 10-thread race test fail. With the trigger in place
  the database itself now also blocks the double booking.
