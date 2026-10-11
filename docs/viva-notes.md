# Viva Notes - Design Decisions in Plain Language

## The big picture

```
 developer ── git commit ──> repo (feature/* -> develop -> main, tags vX.Y.Z)
                               │  Jenkins polls every ~5 min (or Build with Parameters)
                               v
 Jenkins: Checkout -> Install -> flake8 -> Unit+integration -> Selenium
          -> Package source -> Build images -> Push to registry -> Deploy -> Health check
                 │ any failure stops here (later stages skipped)          │
                 v                                                         v
       JUnit report + screenshots                docker compose: nginx -> gunicorn -> SQLite volume

 Ansible: fresh Ubuntu server -> Docker installed -> same containers -> /health checked
          rollback.yml -> previous release image -> /health checked
```

**30-second pitch:** "Guests book hotel rooms through a Flask portal. Every
commit goes through Jenkins: lint, 90 automated tests including 5 Selenium
browser journeys. Only if everything passes do we build Docker images tagged
with version and commit, push them to a registry, deploy them behind Nginx
and check `/health` reports exactly that version. Ansible sets up a fresh
server the same way, a second run changes nothing, and one command rolls
back to the previous release."

## Application

| Question | Answer |
|---|---|
| Why layers (controller/service/DAO/model)? | Each has one job. SQL lives only in DAOs, rules only in services, HTTP only in controllers. Changing the database touches only DAOs; services can be tested without a browser. |
| Why Flask? | Small, explicit, easy to read; the whole request flow is visible. |
| Why SQLite? | Built into Python, zero setup, a single file - enough for one hotel. Limitation: one writer at a time, so it does not scale to many servers. |
| How is double booking prevented? | Three layers: (1) the service checks availability; (2) the check and insert run in one `BEGIN IMMEDIATE` transaction, which takes the write lock first, so concurrent requests queue up; (3) a database **trigger** refuses any overlapping active booking - even from code that skips the service. A test fires 10 threads at once and asserts exactly 1 booking. |
| What is "overlap"? | Existing stay overlaps new stay if `existing.check_in < new.check_out AND existing.check_out > new.check_in`. Check-out day = next guest's check-in day is allowed. |
| Why PENDING then CONFIRMED? | Makes "request", "confirmation" and "status tracking" real, separate steps. PENDING already holds the room. |
| How are invalid state changes prevented? | `UPDATE ... SET status=? WHERE id=? AND status IN (allowed)` - check and change in one atomic statement, plus a `CHECK` constraint on the allowed values. |
| Password storage? | Salted hash (Werkzeug, scrypt). Never the password itself. |
| What is CSRF and how did you stop it? | Another website could make your logged-in browser post "cancel booking 5" to us. Every form carries a random token stored in your session; a POST without the matching token gets HTTP 400. Plus `SameSite=Lax` cookies. |
| Other security measures? | HttpOnly session cookie, no open redirects after login, other users' bookings return 404, `SECRET_KEY` required outside dev/test, secrets only in env vars / Jenkins credentials, audit logs without passwords. |
| Why "not found" for other users' bookings? | Doesn't reveal which booking IDs exist. |
| Why config from environment variables? | Same code and same Docker image in every environment (12-factor). Secrets never in git. |
| Why `/health`? | One URL that Docker, Jenkins and Ansible use to ask "is the app up, can it reach the DB, and which version is it?". |
| Known limitations | PENDING never expires, no admin UI, no payments, HTTP only in the demo, single SQLite server. |

## Testing

| Question | Answer |
|---|---|
| Unit vs integration vs E2E? | Unit (59) check rules on the service layer and database. Integration (26) call the real HTTP routes through Flask's test client. E2E (5) click through the real UI in Chrome. Many fast tests, few slow ones = the test pyramid. |
| Why a temporary database per test? | Tests stay independent and repeatable; order doesn't matter. |
| Why freeze "today"? | Date rules ("not in the past") would otherwise give different results on different days. |
| Why explicit waits, not sleep? | `WebDriverWait` continues as soon as the element appears: faster and less flaky. |
| Why element ids? | Stable selectors: changing the layout does not break the tests. |
| Screenshot on failure? | A pytest hook records each test's result; the browser fixture saves a PNG + HTML when the test failed. Jenkins archives them. |
| How do I know the tests catch bugs? | The deliberate defect (`<` -> `<=` in the overlap SQL) made `test_overlap_rules` fail in Jenkins build #2. Earlier, removing the transaction made the race test fail (now the trigger also protects against that). |
| Is Selenium run "through Maven"? | No - these are Python tests run by pytest, which writes the same JUnit XML that Maven would; Jenkins displays it. Using Maven would need a Java project that doesn't exist. |

## Git

| Question | Answer |
|---|---|
| Branching model? | `main` = releases only (tagged), `develop` = integration, `feature/*` / `fix/*` per change, `experiment/*` never merged. Merges use `--no-ff` so each feature stays visible as a unit. |
| Tell me about the merge conflict. | Two features (contact footer, release footer) were built in parallel from the same commit and both added a footer in the same place. Git couldn't decide, so it marked 3 files. I kept both features: both lines, one CSS rule, both tests; ran flake8 + all tests, then committed the merge `8728b62`. |
| What are tags for? | `v1.0.0`, `v1.1.0` mark exact released commits on `main`. The `VERSION` file goes into the image and `/health`. |
| Where are the PRs? | Merged locally; the repo isn't on GitHub yet, so the PR texts are prepared in `docs/pull-requests/`. |

## Docker

| Question | Answer |
|---|---|
| Why copy requirements.txt before the code? | Layer caching: dependencies re-install only when requirements change. |
| Why `python:3.11-slim`? | Small image, same Python as the pipeline. |
| Why a non-root user? | Limits damage if the app is compromised (`docker exec ... whoami` -> appuser). |
| Why a volume for /data? | Containers are disposable; the database must survive re-creation and upgrades. Shown in the lifecycle demo: new container, old account still logs in. |
| Why Nginx in front of Gunicorn? | Nginx handles slow clients, serves static files, and is the single public entry point; Gunicorn just runs Python. The app port is not published at all. |
| HEALTHCHECK? | Docker marks the container healthy only when /health answers; compose starts nginx only after that, and `--wait` makes deploys fail if the app never becomes healthy. |
| Image vs container? | Image = read-only template (like a class); container = a running instance (like an object). |
| What is `certs/` for? | Antivirus HTTPS scanning on my laptop re-signs HTTPS; containers don't trust it, so downloads failed. Putting that root certificate in `certs/` makes the images trust it. Normally the folder is empty. |

## Jenkins

| Question | Answer |
|---|---|
| How does a failing test fail the pipeline? | pytest exits non-zero, so the `sh` step fails, the stage fails, later stages are skipped. `post { always { junit ... } }` still publishes results. |
| What is the quality gate? | The stage order: deploy only comes after lint + all tests. Demonstrated by build #2 - the defect was caught and staging kept the old version. |
| The parameter? | `APP_ENV` (staging/prod) sets the app's environment, the host port (8081/8082) and the compose project (separate containers + data per environment). Also `BRANCH` and `REGISTRY`. |
| Why tag images with version + commit? | `1.1.0-d07929b`: every image is traceable to one commit, and rollback = redeploy an older tag. The health check compares the commit, so we know the tested commit is the one running. |
| Where are the artifacts? | Source tarball + sha256 checksum (`git archive`, only committed files), two Docker images in the registry, test reports, `deployment.txt`. |
| Where is the secret? | Jenkins credential `hotel-secret-key`, injected with `withCredentials` only where needed and masked in logs. |
| Why poll and not a webhook? | GitHub can't reach Jenkins on localhost. With a public Jenkins you'd add a webhook to `/github-webhook/`. |
| Why `disableConcurrentBuilds`? | Two deploys at once would fight over the same containers. |
| Jenkins in Docker? | Uses the host's Docker through the mounted socket ("Docker outside of Docker"), so built images and deployed containers live on the host. |
| A bug you found in your own pipeline? | Build #2's report showed 5 E2E tests passed although that stage was skipped: an old XML file left in the workspace. Fix: delete `reports/` at checkout; build #9 confirmed it. |

## Ansible

| Question | Answer |
|---|---|
| Inventory? | Which servers to manage, grouped (`[web]`). |
| group_vars? | Settings for every server in a group (app_dir, port, env, version, secret). |
| Idempotent? | Each task describes a desired state ("Docker is installed"), not an action. A second run reports `changed=0` (run 3). Images are only rebuilt when the release/commit changes, because even a cached rebuild gets a new image id. |
| become? | Run tasks with sudo. |
| no_log? | Keeps the SECRET_KEY out of Ansible's output. |
| How does rollback work? | Every release's images stay on the server, tagged with the version. `rollback.yml` points `.env` at the previous tag, restarts with `--no-build`, and asserts `/health` shows that version. Verified + 5/5 Selenium journeys on the restored release. |
| Why `--check`? | Dry run: shows what would change without changing it. |
| Why no Galaxy collections? | Only built-in modules: nothing extra to install. |
| Where did you run it? | In a disposable Ubuntu 24.04 container with systemd + SSH acting as the server (no VM available). Honest limitation: not tested on a real VM. |
