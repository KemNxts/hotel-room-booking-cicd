# Task 12 - command sheet

**Task 12 - Jenkins-Docker Continuous Deployment**

## Before you start

- Docker Desktop, Jenkins and the registry running (`cd deploy\jenkins; docker compose up -d`), and at least one successful build of the job that deployed to staging (it was build #12 in this recording, started live in the Task 8 video).
- The admin password is read from deploy/jenkins/.env by the commands; never show that file.
- Port 8081 is the staging environment (prod is 8082).

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | From a tested commit to a deployed release: the last build | `$jh = @{ Authorization = 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('admin:' + ((Get-Content deploy/jenkins/.env \| Where-Object { $_ -like 'JENKINS_ADMIN_PASSWORD=*' }) -replace '^[^=]+=', ''))) }; $b = Invoke-RestMethod 'http://localhost:8090/job/hotel-booking/lastBuild/api/json?tree=number,displayName,result' -Headers $jh; $tag = $b.displayName -replace '^#\d+ ', ''; "last build: #$($b.number)   $($b.displayName)   $($b.result)"; (Invoke-RestMethod 'http://localhost:8090/job/hotel-booking/lastBuild/wfapi/describe' -Headers $jh).stages \| Select-Object name, status \| Format-Table -AutoSize` | 'last build: #12   #12 1.1.0-1c2103c   SUCCESS' and the stages Checkout ... Unit & integration tests, E2E tests, Package source, Build images, Publish images, Deploy, Health check, all SUCCESS. |
| 2 | Versioned image tags: version plus commit SHA | `'VERSION file   : ' + (Get-Content VERSION); 'commit (develop): ' + (git rev-parse --short develop); 'tag I compute  : ' + (Get-Content VERSION) + '-' + (git rev-parse --short develop); 'tag of the build: ' + $tag; Select-String -Path Jenkinsfile -Pattern 'env.IMAGE_TAG\|env.GIT_SHORT' \| Select-Object -First 2 \| ForEach-Object { $_.Line.Trim() }` | Version 1.1.0, commit 1c2103c (or the current one), and the same tag 1.1.0-1c2103c computed two ways, plus the two Jenkinsfile lines that build it. |
| 3 | Build and push, as recorded in the Jenkins log | `(Invoke-WebRequest 'http://localhost:8090/job/hotel-booking/lastBuild/consoleText' -Headers $jh -UseBasicParsing).Content -split '\r?\n' \| Select-String '\+ docker build -\|\+ docker push\|digest:' \| ForEach-Object { $_.Line -replace '^\[[^\]]+\]\s*', '' }` | Two 'docker build -t localhost:5000/hotel-booking-...' lines with the build arguments, two 'docker push' lines and the two digests (sha256:...). |
| 4 | The local registry and all published releases | `'repositories: ' + ((Invoke-RestMethod http://localhost:5000/v2/_catalog).repositories -join ', '); 'tags of hotel-booking-app:'; (Invoke-RestMethod http://localhost:5000/v2/hotel-booking-app/tags/list).tags \| Sort-Object` | hotel-booking-app and hotel-booking-nginx, and eight tags such as 1.0.0-64351fe ... 1.1.0-1c2103c. |
| 5 | The commit is inside the image | `(docker image inspect "localhost:5000/hotel-booking-app:$tag" \| ConvertFrom-Json).Config.Labels \| Format-List` | org.opencontainers.image.revision = the commit (1c2103c), org.opencontainers.image.version = 1.1.0, title hotel-booking-app. |
| 6 | Deployment: a fresh container | `(Invoke-WebRequest 'http://localhost:8090/job/hotel-booking/lastBuild/consoleText' -Headers $jh -UseBasicParsing).Content -split '\r?\n' \| Select-String 'docker compose (pull\|up)\|Container hotel-staging-app-1 (Recreate\|Started\|Healthy)\|Deployed ' \| ForEach-Object { $_.Line -replace '^\[[^\]]+\]\s*', '' }` | '+ docker compose pull', '+ docker compose up -d --no-build --wait ...', 'Container hotel-staging-app-1 Recreated / Started / Healthy' and 'Deployed 1.1.0-... to staging: http://localhost:8081'. |
| 7 | The running container is the published image | `docker ps --filter name=hotel-staging --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'; 'running container image id: ' + (docker inspect hotel-staging-app-1 --format '{{.Image}}'); 'registry tag image id     : ' + (docker image inspect "localhost:5000/hotel-booking-app:$tag" --format '{{.Id}}')` | hotel-staging-app-1 and hotel-staging-nginx-1 Up (healthy), staging port 8081, and two identical sha256 image ids. |
| 8 | Health verification: version and commit | `curl.exe -s http://localhost:8081/health; ''; 'commit at the tip of develop: ' + (git rev-parse --short develop); 'health.json saved by Jenkins:'; Invoke-RestMethod 'http://localhost:8090/job/hotel-booking/lastBuild/artifact/reports/health.json' -Headers $jh \| ConvertTo-Json -Compress` | {"commit":"1c2103c","env":"staging","status":"ok","version":"1.1.0"}, the same commit as develop, and the same JSON in health.json. |
| 9 | Docker Hub: the honest status | `Select-String -Path Jenkinsfile -Pattern 'startsWith\|registry-creds\|docker login\|name: .REGISTRY' \| ForEach-Object { '{0,3}: {1}' -f $_.LineNumber, $_.Line.Trim() }` | The REGISTRY parameter, the startsWith('localhost') test, withCredentials registry-creds and the docker login line. |

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- List every published release (these are the rollback candidates):

  ```powershell
  (Invoke-RestMethod http://localhost:5000/v2/hotel-booking-app/tags/list).tags | Sort-Object
  ```

- Open the staging site:

  ```powershell
  Start-Process http://localhost:8081
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| The registry answers nothing on port 5000 | `docker ps --filter name=registry`; start it with `cd deploy\jenkins; docker compose up -d`. If the Task 3 demo server is still running on 5000, stop it first. |
| staging containers are not running / port 8081 does not answer | Run the Jenkins job once more (Build with Parameters, APP_ENV=staging) or `cd` to the repo and start the stack with the tag of the last build: `$env:IMAGE_PREFIX='localhost:5000/'; $env:IMAGE_TAG='1.1.0-<commit>'; $env:HOST_PORT='8081'; $env:SECRET_KEY='<any long text>'; docker compose -p hotel-staging up -d --no-build`. |
| HTTP 401 from the Jenkins API | The JENKINS_ADMIN_PASSWORD line in deploy/jenkins/.env is wrong. Use the one Jenkins was first started with. |
| The tag in the video does not match yours | Your last build has another commit. The commands compute the tag from the last build's name, so use them unchanged. |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 12
```
