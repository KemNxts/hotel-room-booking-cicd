## What does this PR do?

<!-- Short summary: what changed and why. -->

Closes #

## How was it tested?

<!-- Commands run and results, e.g. "pytest: 90 passed". -->

## Author checklist

- [ ] Branch name follows `feature/<short-description>` (or `fix/...`)
- [ ] Commit messages follow the convention in CONTRIBUTING.md
- [ ] `flake8` is clean
- [ ] Tests added/updated and passing (`pytest` - unit, integration and e2e)
- [ ] Jenkins pipeline is green for this branch
- [ ] No secrets, `.env` files or database files committed
- [ ] README/docs updated if run/setup steps changed

## Reviewer checklist

- [ ] Layering respected: no SQL outside `app/dao/`, no HTTP in services
- [ ] Inputs validated on the server, not only in the browser
- [ ] Booking ownership checked for anything a user can view or change
- [ ] New POST forms include `csrf_token`
- [ ] Tests would fail if the change were broken
