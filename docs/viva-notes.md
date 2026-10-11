# Viva Notes - Design Decisions in Plain Language

## The big picture

```
 developer ── git commit ──> repo (feature/* -> develop -> main)
                               │  Jenkins polls every ~5 min
                               v
 Jenkins: Checkout -> Build -> Unit tests -> E2E tests -> Package -> Deploy
                                   │ any failure stops here      │
                                   v                             v
                        JUnit report + screenshots     docker compose: nginx -> gunicorn -> SQLite volume

 Ansible: fresh Ubuntu server -> Docker installed -> same containers running
```

## Application

| Question | Answer |
|---|---|
| Why layers (controller/service/DAO/model)? | Each has one job. SQL lives only in DAOs, rules only in services, HTTP only in controllers. Changing the database touches only DAOs; services can be tested without a browser. |
| Why Flask? | Small, explicit, easy to read; the whole request flow is visible. |
| Why SQLite? | Built into Python, zero setup, a single file - enough for an MVP. Limitation: one writer at a time, so it does not scale to many servers. |
| How is double booking prevented? | The availability check and insert run in one `BEGIN IMMEDIATE` transaction, which takes the write lock first, so concurrent requests run one after another. A unit test fires 10 threads at once and asserts exactly 1 booking. |
| What is "overlap"? | Existing stay overlaps new stay if `existing.check_in < new.check_out AND existing.check_out > new.check_in`. Check-out day = next check-in day is allowed. |
| Why PENDING then CONFIRMED? | Makes "request", "confirmation" and "status tracking" real, separate steps. PENDING already holds the room. |
| Password storage? | Salted hash (Werkzeug, scrypt). Never the password itself. |
| Why "not found" for other users' bookings? | Doesn't reveal which booking IDs exist. |
| Why config from environment variables? | Same code and same Docker image in every environment (12-factor). Secrets never in git. |
| Why `/health`? | One URL that Docker, Jenkins and Ansible use to ask "is the app up and can it reach the DB?". |
| Known limitations | No CSRF tokens, PENDING never expires, no admin UI, no payments. |

## Testing

| Question | Answer |
|---|---|
| Unit vs E2E? | Unit tests (49, ~7s) check business rules directly on the service layer. E2E tests (5, ~25s) click through the real UI in Chrome. Many fast tests, few slow ones = the test pyramid. |
| Why a temporary database per test? | Tests stay independent and repeatable; order doesn't matter. |
| Why freeze "today"? | Date rules ("not in the past") would otherwise give different results on different days. |
| Why explicit waits, not sleep? | `WebDriverWait` continues as soon as the element appears: faster and less flaky. |
| Screenshot on failure? | A pytest hook records each test's result; the browser fixture saves a PNG + HTML when the test failed. Jenkins archives them. |
| How do I know the tests catch bugs? | We changed `<` to `<=` in the overlap SQL and removed the transaction; tests failed both times. |

## Docker

| Question | Answer |
|---|---|
| Why copy requirements.txt before the code? | Layer caching: dependencies re-install only when requirements change. |
| Why `python:3.11-slim`? | Small image, same Python as development. |
| Why a non-root user? | Limits damage if the app is compromised. |
| Why a volume for /data? | Containers are disposable; the database must survive re-creation and upgrades. |
| Why Nginx in front of Gunicorn? | Nginx handles slow clients, serves static files, and is the single public entry point; Gunicorn just runs Python. The app port is not published at all. |
| Why is the nginx config baked into an image? | Works anywhere without bind mounts - including when Jenkins (in a container) deploys via the host's Docker. |
| HEALTHCHECK? | Docker marks the container healthy only when /health answers; compose starts nginx only after that, and `--wait` makes deploys fail if the app never becomes healthy. |

## Jenkins

| Question | Answer |
|---|---|
| How does a failing test fail the pipeline? | pytest exits non-zero, so the `sh` step fails, the stage fails, later stages are skipped. `post { always { junit ... } }` still publishes results. |
| The parameter? | `APP_ENV` (staging/prod) sets the app's environment, the host port and the compose project name (separate containers + data per environment). |
| Why tag images with the build number? | Every build is traceable, and rollback = redeploy an older tag. |
| Where is the secret? | Jenkins credential `hotel-secret-key`, injected with `withCredentials` only in the Deploy stage and masked in logs. |
| Why `disableConcurrentBuilds`? | Two deploys at once would fight over the same containers. |
| Jenkins in Docker? | Uses the host's Docker through the mounted socket ("Docker outside of Docker"), so built images and deployed containers live on the host. |

## Ansible

| Question | Answer |
|---|---|
| Inventory? | Which servers to manage, grouped (`[web]`). |
| group_vars? | Settings for every server in a group (app_dir, port, env, secret). |
| Idempotent? | Each task describes a desired state ("Docker is installed"), not an action. A second run reports `changed=0`. |
| become? | Run tasks with sudo. |
| no_log? | Keeps the SECRET_KEY out of Ansible's output. |
| Why `--check`? | Dry run: shows what would change without changing it. |
| Why no Galaxy collections? | Only built-in modules: nothing extra to install. |
