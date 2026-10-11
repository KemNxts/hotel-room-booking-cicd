# PR: feature/ci-release-pipeline -> develop

## What does this PR do?

Turns the Jenkinsfile into a full CI/CD pipeline:

Checkout -> Install dependencies -> Static checks (compileall + flake8) ->
Unit & integration tests -> E2E tests (Selenium) -> Package source
(`git archive` + sha256) -> Build images -> Publish images (registry) ->
Deploy (pull + `compose up --wait`) -> Health check (version + commit must match).

- Images and archive tagged `<VERSION>-<commit>`, e.g. `1.0.0-64351fe`.
- Parameters: `APP_ENV` (staging/prod), `BRANCH`, `REGISTRY`.
- Local `registry:2` started with Jenkins; Docker Hub via `registry-creds`.
- Optional `certs/` folder for networks with HTTPS inspection.

## How was it tested?

Jenkins build **#1** of this branch: all 10 stages green, 87 tests,
images pushed to `localhost:5000`, staging `/health` =
`{"commit":"64351fe","env":"staging","status":"ok","version":"1.0.0"}`.
Log: `docs/evidence/jenkins/build-01-green-staging.log`.

## Author checklist

- [x] Branch name, commit convention, flake8 clean, tests passing
- [x] Jenkins pipeline green for this branch (build #1)
- [x] No secrets committed (credentials only via Jenkins `withCredentials`; log checked)
- [x] Docs updated

## Reviewer checklist

- [x] Deploy only after all test stages (stage order + fail-fast)
- [x] Secret never echoed; registry password via `--password-stdin`
- [x] Deployed artifact = tested commit (tag contains the commit SHA, health check compares it)
