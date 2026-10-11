# PR: develop -> main (release v1.1.0)

## What does this PR do?

Releases v1.1.0: "Nights" column in My bookings (`feature/nights-column`)
and `VERSION` bumped to 1.1.0.

## How was it tested?

- Jenkins #6 and #7 on `develop` (staging): green, 90 tests.
- After merge + tag: Jenkins #8 on `main` (prod, port 8082): green, 90 tests,
  `/health` = `{"commit":"d07929b","env":"prod","status":"ok","version":"1.1.0"}`.

## Release checklist

- [x] develop green in Jenkins
- [x] `git merge --no-ff develop` into main, `git tag -a v1.1.0`
- [x] Pipeline deployed main to prod and health check passed
- [x] Rollback path verified (to v1.0.0 and back - `docs/evidence/docker/rollback-prod.txt`)
