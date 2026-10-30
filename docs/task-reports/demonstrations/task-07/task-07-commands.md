# Task 7 - command sheet

**Task 7 - Jenkins Installation and Continuous Integration**

## Before you start

- Docker Desktop running, then Jenkins and the registry started: `cd deploy\jenkins; docker compose up -d` and wait about 60 seconds until http://localhost:8090/login answers.
- The admin password is the `JENKINS_ADMIN_PASSWORD=` line in `deploy/jenkins/.env`. The commands read it themselves; never show that file on screen.
- Open PowerShell in the project folder.
- Jenkins running at http://localhost:8090 (see part 1). Log in as `admin`; the password is the JENKINS_ADMIN_PASSWORD line of deploy/jenkins/.env (do not show that file).
- In the recording the login happens before the video starts, so no password is on screen. Do the same for your demonstration: log in first, then start talking.
- These pages are only read; nothing is saved in the configuration. When you open Configure by hand, leave it without clicking Save.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

### Task 7 (part 1) - Jenkins installation and what is really set up (terminal)

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | Jenkins as a container: the compose file | `Get-Content deploy/jenkins/docker-compose.yml \| Select-String -NotMatch '^\s*#' \| Select-String 'image:\|ports:\|8090\|5000\|jenkins-home\|docker.sock\|/repo\|restart:\|registry' \| ForEach-Object { $_.Line.Trim() }` | The jenkins image, 127.0.0.1:8090:8080, the registry on 5000, the jenkins-home volume, docker.sock, ../..:/repo:ro and restart: unless-stopped. |
| 2 | What is inside the Jenkins image | `Get-Content deploy/jenkins/Dockerfile \| Select-String -NotMatch '^\s*#' \| Select-String 'FROM\|python3.11\|chromium\|docker:\|plugin' \| ForEach-Object { $_.Line.Trim() }; '--- plugins.txt'; Get-Content deploy/jenkins/plugins.txt` | FROM jenkins/jenkins:lts-jdk21, Python 3.11 copied in, chromium and chromium-driver, the Docker CLI, then the six plugins. |
| 3 | Start-up and the running instance | `Select-String -Path docs/05-ci-cd-pipeline.md -Pattern 'docker compose up' \| Select-Object -First 1 \| ForEach-Object { $_.Line }; docker ps --filter name=hotel-jenkins --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'; 'Jenkins version: ' + (Invoke-WebRequest http://localhost:8090/login -UseBasicParsing).Headers['X-Jenkins']` | The documented command, two containers hotel-jenkins-jenkins-1 and hotel-jenkins-registry-1 'Up', and 'Jenkins version: 2.580.1'. |
| 4 | Level 1: the Jenkinsfile exists in Git | `git ls-files Jenkinsfile; git log --oneline -4 -- Jenkinsfile` | 'Jenkinsfile' is tracked, followed by its last four commits. |
| 5 | Level 2: the Jenkins job is configured | `$jh = @{ Authorization = 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('admin:' + ((Get-Content deploy/jenkins/.env \| Where-Object { $_ -like 'JENKINS_ADMIN_PASSWORD=*' }) -replace '^[^=]+=', ''))) }; (Invoke-WebRequest 'http://localhost:8090/job/hotel-booking/config.xml' -Headers $jh -UseBasicParsing).Content -split '\r?\n' \| Select-String 'url>\|name>\*\|scriptPath\|<spec>\|<name>(APP_ENV\|BRANCH\|REGISTRY)' \| ForEach-Object { $_.Line.Trim() }` | <spec>H/5 * * * *</spec>, the parameter names APP_ENV, BRANCH, REGISTRY, <url>file:///repo</url>, <name>*/${BRANCH}</name> and <scriptPath>Jenkinsfile</scriptPath>. |
| 6 | Level 3: the job actually ran, and what happened | `Invoke-RestMethod 'http://localhost:8090/job/hotel-booking/api/json?tree=builds[number,result,displayName]' -Headers $jh \| Select-Object -ExpandProperty builds \| Format-Table number, result, displayName -AutoSize` | Builds #1 to #11 with their result: SUCCESS for most, FAILURE for #2 and #9, each named version-commit. |
| 7 | The stages of build 11 | `(Invoke-RestMethod 'http://localhost:8090/job/hotel-booking/11/wfapi/describe' -Headers $jh).stages \| Select-Object name, status, @{ n = 'seconds'; e = { [int]($_.durationMillis / 1000) } } \| Format-Table -AutoSize` | Eleven stages, each SUCCESS, e.g. Unit & integration tests 19s, E2E tests 20s, Build images 15s, Deploy 12s. |
| 8 | Proof in the log: install, lint, tests, packaging | `(Invoke-WebRequest 'http://localhost:8090/job/hotel-booking/11/consoleText' -Headers $jh -UseBasicParsing).Content -split '\r?\n' \| Select-String 'Building commit\|Python 3\|pip install\|flake8\|passed\|sha256sum hotel\|Finished:' \| ForEach-Object { $_.Line.Trim() -replace '^\[[^\]]+\]\s*', '' }` | Building commit 1c2103c on develop, Python 3.11, pip install, flake8, '85 passed', '5 passed, 85 deselected', sha256sum, Finished: SUCCESS. |

### Task 7 (part 2) - The Jenkins web interface: job, configuration, build, console, tests, artifacts

| # | Step | Command / action | Expected result |
|---|---|---|---|

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- Open Jenkins in the browser:

  ```powershell
  Start-Process http://localhost:8090
  ```

- Jenkins logs:

  ```powershell
  docker logs hotel-jenkins-jenkins-1 --tail 30
  ```

- Open the job page in your own browser:

  ```powershell
  Start-Process http://localhost:8090/job/hotel-booking/
  ```

- See why a build was triggered (Git polling log):

  ```powershell
  Start-Process http://localhost:8090/job/hotel-booking/scmPollLog/
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| `docker` commands fail (pipe not found) | Start Docker Desktop and wait for 'Engine running'. |
| http://localhost:8090 does not answer | `cd deploy\jenkins; docker compose ps`. If the containers are not Up: `docker compose up -d`, then wait about a minute (Jenkins needs time to start). Check `docker logs hotel-jenkins-jenkins-1 --tail 30`. |
| HTTP 401 / 403 from the API | The password in deploy/jenkins/.env is missing or was changed after the first start. Jenkins keeps the first password in its volume; check the JENKINS_ADMIN_PASSWORD line, or reset the lab with `docker compose down -v` (this deletes all Jenkins history). |
| No builds listed | The job has not run yet (or the jenkins-home volume was deleted). Open the job and click 'Build with Parameters'. |
| Login page keeps coming back | Wrong password. Use the JENKINS_ADMIN_PASSWORD line of deploy/jenkins/.env. |
| 'Jenkins is getting ready to work' or a blank page | Jenkins is still starting. Wait a minute and press F5. |
| The job hotel-booking is missing | The jenkins-home volume was deleted. Restart Jenkins (`docker compose up -d` in deploy/jenkins); the job is recreated by init.groovy.d/01-setup.groovy, but the old build history is gone. |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 07 -Part cli
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 07 -Part ui
```
