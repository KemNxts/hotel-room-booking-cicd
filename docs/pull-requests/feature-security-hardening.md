# PR: feature/security-hardening -> develop

## What does this PR do?

Hardens the MVP before the first release:

- CSRF token on every form; POST without a valid token -> HTTP 400.
- Session cookie `HttpOnly` + `SameSite=Lax` (`Secure` switchable via `SESSION_COOKIE_SECURE=1`).
- Audit log lines for registrations, logins, failed logins and booking status changes (no passwords or emails).
- `/health` also reports `version` and `commit`.
- SQLite triggers reject overlapping active bookings at the database level.
- New `tests/integration/` suite (Flask test client) + database rule tests.

Closes #HB-06 (replace with the GitHub issue number)

## How was it tested?

- `flake8`: clean
- `pytest -m "not e2e"`: 82 passed
- `pytest -m e2e`: 5 passed (forms still work with CSRF tokens)

## Author checklist

- [x] Branch name follows `feature/<short-description>`
- [x] Commit messages follow CONTRIBUTING.md (`feat:`, `test:`)
- [x] `flake8` is clean
- [x] Tests added and passing (87 total)
- [ ] Jenkins pipeline green for this branch - pipeline not yet extended at this point; verified on develop in Jenkins build #1 onward
- [x] No secrets committed
- [x] Docs updated

## Reviewer checklist

- [x] No SQL outside `app/dao/` (trigger lives in `schema.sql`)
- [x] Server-side validation covered by `test_invalid_registration_is_rejected_server_side`
- [x] Ownership: `test_other_users_cannot_see_confirm_or_cancel_my_booking`
- [x] All POST forms include `csrf_token` (6 forms)
- [x] Tests fail if broken: `test_post_without_csrf_token_is_rejected` and `test_post_with_wrong_csrf_token_is_rejected` check the 400 response
