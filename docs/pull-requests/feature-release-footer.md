# PR: feature/release-footer -> develop

## What does this PR do?

Shows "Release <version> · <environment>" in every page footer, so a
deploy or rollback can be checked in the browser.

## Merge conflict

`feature/contact-footer` was merged first and added a footer in the same
place. The merge reported conflicts in `base.html`, `style.css` and
`test_routes.py` (output: `docs/evidence/git/merge-conflict.txt`).

Resolution: keep both footer lines (contact first, release second), one
combined CSS rule, both tests. Merge commit `8728b62`.

## How was it tested?

After resolving: `flake8` clean, `pytest`: **89 passed**.
New test: `test_footer_shows_the_running_release`.

## Author checklist

- [x] Branch name, commit convention, flake8 clean
- [x] Tests added and passing
- [x] Jenkins: develop green after merge (build #4)
- [x] No secrets committed

## Reviewer checklist

- [x] Conflict resolution keeps BOTH features (checked in the browser screenshot `docs/evidence/screenshots/app-07-my-bookings-status.png`)
- [x] No conflict markers left (`grep -rn "<<<<<<<" app tests` -> none)
