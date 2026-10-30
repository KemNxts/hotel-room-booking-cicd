# Task 8 - command sheet

**Task 8 - Pipeline as Code and Server Deployment**

## Before you start

- Nothing needs to be running for this part: it only reads the Jenkinsfile.
- Open PowerShell in the project folder, or open Jenkinsfile in VS Code and scroll.
- Jenkins and the registry running (`cd deploy\jenkins; docker compose up -d`), Docker Desktop running.
- This part starts a REAL build of the `develop` branch and deploys it to STAGING (http://localhost:8081). It takes about 2 minutes. It does not touch prod, GitHub or Docker Hub.
- Jenkins builds committed code from the repository mounted at /repo: commit your changes first if you want them in the build.
- Log in to Jenkins before the demo so the password is not typed in front of the examiner.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

### Task 8 (part 1) - Pipeline as code: the Jenkinsfile, stage by stage

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | The Jenkinsfile and the quality gate | `Get-Content Jenkinsfile \| Select-Object -First 16` | The header comment with the stage flow and the quality gate explanation, plus the agent and credentials requirements. |
| 2 | Parameters and the polling trigger | `Get-Content Jenkinsfile \| Select-Object -Skip 18 -First 18` | parameters { choice APP_ENV [staging, prod]; string BRANCH develop; string REGISTRY localhost:5000 } and triggers { pollSCM('H/5 * * * *') }. |
| 3 | Options and environment variables | `Get-Content Jenkinsfile \| Select-Object -Skip 37 -First 15` | options { timestamps, buildDiscarder 20, disableConcurrentBuilds, timeout 30 min } and environment { PYTHON, HOST_PORT staging 8081 / prod 8082, COMPOSE_PROJECT_NAME hotel-<env> }. |
| 4 | Stage 1: Checkout | `Get-Content Jenkinsfile \| Select-Object -Skip 54 -First 21` | checkout scm, 'rm -rf reports dist', APP_VERSION from the VERSION file, GIT_SHORT, IMAGE_TAG = version-commit, build display name. |
| 5 | Stages 2 and 3: install and static checks | `Get-Content Jenkinsfile \| Select-Object -Skip 75 -First 23` | Install: python3.11 -m venv, pip install -r requirements-dev.txt. Static checks: compileall and flake8. |
| 6 | Stages 4 and 5: the tests, the quality gate | `Get-Content Jenkinsfile \| Select-Object -Skip 98 -First 14` | 'pytest tests/unit tests/integration --junitxml=reports/unit-integration-tests.xml' and 'pytest -m e2e --junitxml=reports/e2e-tests.xml'. |
| 7 | Stage 6: package the source with a checksum | `Get-Content Jenkinsfile \| Select-Object -Skip 112 -First 14` | git archive ... hotel-booking-$IMAGE_TAG.tar.gz and sha256sum written to a .sha256 file. |
| 8 | Stage 7: build the Docker images | `Get-Content Jenkinsfile \| Select-Object -Skip 126 -First 14` | docker build -t ${IMAGE_PREFIX}hotel-booking-app:$IMAGE_TAG with --build-arg APP_VERSION and GIT_COMMIT, and the nginx image. |
| 9 | Stage 8: publish the images to the registry | `Get-Content Jenkinsfile \| Select-Object -Skip 140 -First 22` | docker push for app and nginx; if the registry starts with localhost no login, else withCredentials registry-creds and docker login. |
| 10 | Stage 9: deploy | `Get-Content Jenkinsfile \| Select-Object -Skip 162 -First 14` | withCredentials hotel-secret-key; docker compose pull; docker compose up -d --no-build --wait --wait-timeout 120. |
| 11 | Stage 10: health check and version verification | `Get-Content Jenkinsfile \| Select-Object -Skip 176 -First 17` | wget /health inside the nginx container, saved to reports/health.json, then grep for the exact version and commit. |
| 12 | The deployment record and post actions | `Get-Content Jenkinsfile \| Select-Object -Skip 193 -First 28` | reports/deployment.txt content, then post { always { junit + archiveArtifacts }, success { echo Deployed ... }, failure { echo FAILED - nothing was deployed } }. |
| 13 | The stage order is the quality gate | `Select-String -Path Jenkinsfile -Pattern "stage\('" \| ForEach-Object { '{0,3}: {1}' -f $_.LineNumber, $_.Line.Trim() }` | Ten stages: Checkout, Install dependencies, Static checks, Unit & integration tests, E2E tests (Selenium), Package source, Build images, Publish images, Deploy, Health check. |

### Task 8 (part 2) - A live pipeline run in Jenkins: source to deployed staging

| # | Step | Command / action | Expected result |
|---|---|---|---|

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- List all stages with their line numbers:

  ```powershell
  Select-String -Path Jenkinsfile -Pattern "stage\('" | ForEach-Object { '{0,3}: {1}' -f $_.LineNumber, $_.Line.Trim() }
  ```

- Read the pipeline documentation:

  ```powershell
  Get-Content docs/05-ci-cd-pipeline.md
  ```

- Start the same build from a terminal instead of the browser (uses the API and your password from .env; the commands do not print it):

  ```powershell
  # open http://localhost:8090/job/hotel-booking/build?delay=0sec and click Build
  ```

- Check what the pipeline deployed:

  ```powershell
  curl.exe -s http://localhost:8081/health
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| Line numbers in the commands do not match your Jenkinsfile | The file was edited. Open it in VS Code and scroll to the stage; or find a stage with `Select-String -Path Jenkinsfile -Pattern "stage\('"` and use its line number in -Skip / -First. |
| The build fails at 'Install dependencies' with CERTIFICATE_VERIFY_FAILED | Antivirus HTTPS scanning inside the container. Put your antivirus root certificate in certs/ as a .crt file and rebuild the Jenkins image: `cd deploy\jenkins; docker compose up -d --build`. |
| The build fails at 'Deploy' (port 8081 in use) | Another program uses 8081. `Get-NetTCPConnection -LocalPort 8081 -State Listen` shows it; stop it and re-run the build. |
| 'permission denied ... docker.sock' | Linux host only: set DOCKER_GID in deploy/jenkins/.env. |
| A test stage fails | That is the quality gate working. Read the Console Output and the Test Result page, fix the code, commit, and build again. |
| Build waits in the queue | Only one build runs at a time (disableConcurrentBuilds). Wait for the running build to finish. |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 08 -Part code
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 08 -Part live
```
