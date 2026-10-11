# Contributing Guide

## Branching model

| Branch        | Purpose                                              | Who merges into it            |
|---------------|------------------------------------------------------|-------------------------------|
| `main`        | Production-ready code. Every commit is deployable.   | Only `develop` (via PR)       |
| `develop`     | Integration branch. Features meet here and get tested together. | `feature/*` branches (via PR) |
| `feature/*`   | One branch per feature or fix, cut from `develop`.   | -                             |

Branch naming rules:

- Lowercase, words separated by hyphens: `feature/<short-description>`
- Optionally prefix the issue number: `feature/12-booking-cancellation`
- Bug fixes use the same pattern: `feature/fix-login-redirect`

Typical flow:

```bash
git checkout develop
git pull
git checkout -b feature/booking-cancellation
# ... work, commit ...
git push -u origin feature/booking-cancellation
# open a Pull Request: feature/booking-cancellation -> develop
```

Release: open a PR `develop -> main` once the CI pipeline is green on `develop`.

## Commit messages

Format (based on Conventional Commits):

```
<type>: <short summary in imperative mood, max ~60 chars>

<optional body: WHY the change was made, not just what>
```

Allowed types:

| Type       | Use for                                   |
|------------|-------------------------------------------|
| `feat`     | New user-facing feature                   |
| `fix`      | Bug fix                                   |
| `test`     | Adding or changing tests                  |
| `docs`     | Documentation only                        |
| `refactor` | Code change that is not a fix or feature  |
| `ci`       | Jenkinsfile / pipeline changes            |
| `build`    | Dependencies, Dockerfile, packaging       |
| `chore`    | Repo housekeeping                         |

Examples:

- `feat: add booking cancellation endpoint`
- `fix: reject check-out date before check-in`
- `ci: fail pipeline when pytest reports failures`

## Pull requests

- Link the issue (`Closes #12`).
- The CI pipeline must pass before merge.
- Fill in the PR template checklist.
