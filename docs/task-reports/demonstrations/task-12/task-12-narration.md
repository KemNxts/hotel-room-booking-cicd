# Task 12 - narration script

**Task 12 - Jenkins-Docker Continuous Deployment**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

## Step 1 - From a tested commit to a deployed release: the last build [video 00:01]

**What I am doing:** running

```powershell
$jh = @{ Authorization = 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('admin:' + ((Get-Content deploy/jenkins/.env | Where-Object { $_ -like 'JENKINS_ADMIN_PASSWORD=*' }) -replace '^[^=]+=', ''))) }; $b = Invoke-RestMethod 'http://localhost:8090/job/hotel-booking/lastBuild/api/json?tree=number,displayName,result' -Headers $jh; $tag = $b.displayName -replace '^#\d+ ', ''; "last build: #$($b.number)   $($b.displayName)   $($b.result)"; (Invoke-RestMethod 'http://localhost:8090/job/hotel-booking/lastBuild/wfapi/describe' -Headers $jh).stages | Select-Object name, status | Format-Table -AutoSize
```

**Spoken script (as in the video):**

> This is Task 12, Jenkins and Docker continuous deployment. Continuous deployment means that every change that passes the tests is delivered automatically. Here is the proof from the build I started live in the previous video. The command reads the admin password from the environment file without showing it. The latest build is number twelve, named with the version and the commit, and the result is success. The stages show the quality gate: the tests come first, and the images are built, published and deployed only after them.

**What the output means:** 'last build: #12   #12 1.1.0-1c2103c   SUCCESS' and the stages Checkout ... Unit & integration tests, E2E tests, Package source, Build images, Publish images, Deploy, Health check, all SUCCESS.

**What I will tell the professor:** "Only after the tests passed did the build create the images and deploy them."

## Step 2 - Versioned image tags: version plus commit SHA [video 00:41]

**What I am doing:** running

```powershell
'VERSION file   : ' + (Get-Content VERSION); 'commit (develop): ' + (git rev-parse --short develop); 'tag I compute  : ' + (Get-Content VERSION) + '-' + (git rev-parse --short develop); 'tag of the build: ' + $tag; Select-String -Path Jenkinsfile -Pattern 'env.IMAGE_TAG|env.GIT_SHORT' | Select-Object -First 2 | ForEach-Object { $_.Line.Trim() }
```

**Spoken script (as in the video):**

> How is the release identified? The tag of every image is the version from the VERSION file, a dash, and the short commit id. Here are the three pieces: the version, the commit at the tip of develop, and the tag I compute from them, which is exactly the tag of the build. The Jenkinsfile builds it in the checkout stage. So the tag tells you which release and which commit an image contains.

**What the output means:** Version 1.1.0, commit 1c2103c (or the current one), and the same tag 1.1.0-1c2103c computed two ways, plus the two Jenkinsfile lines that build it.

**What I will tell the professor:** "Every image carries the version and the commit it was built from."

## Step 3 - Build and push, as recorded in the Jenkins log [video 01:12]

**What I am doing:** running

```powershell
(Invoke-WebRequest 'http://localhost:8090/job/hotel-booking/lastBuild/consoleText' -Headers $jh -UseBasicParsing).Content -split '\r?\n' | Select-String '\+ docker build -|\+ docker push|digest:' | ForEach-Object { $_.Line -replace '^\[[^\]]+\]\s*', '' }
```

**Spoken script (as in the video):**

> Now the Jenkins log. Docker build creates the application image with the registry prefix and the tag, and passes the version and the commit as build arguments. Then docker push publishes it to the local registry, and the registry answers with a digest, a unique fingerprint of the image. The same happens for the Nginx image.

**What the output means:** Two 'docker build -t localhost:5000/hotel-booking-...' lines with the build arguments, two 'docker push' lines and the two digests (sha256:...).

**What I will tell the professor:** "The log shows the images built with the version and commit and pushed to the registry."

## Step 4 - The local registry and all published releases [video 01:39]

**What I am doing:** running

```powershell
'repositories: ' + ((Invoke-RestMethod http://localhost:5000/v2/_catalog).repositories -join ', '); 'tags of hotel-booking-app:'; (Invoke-RestMethod http://localhost:5000/v2/hotel-booking-app/tags/list).tags | Sort-Object
```

**Spoken script (as in the video):**

> The registry itself. I ask it directly, over its HTTP interface, which repositories it holds: the application and Nginx. And which tags the application has: every release that the pipeline ever published, version and commit. The new one is among them. These older tags are also the candidates for a rollback, because nothing has to be rebuilt.

**What the output means:** hotel-booking-app and hotel-booking-nginx, and eight tags such as 1.0.0-64351fe ... 1.1.0-1c2103c.

**What I will tell the professor:** "The registry keeps every published release, which makes rollback possible."

## Step 5 - The commit is inside the image [video 02:10]

**What I am doing:** running

```powershell
(docker image inspect "localhost:5000/hotel-booking-app:$tag" | ConvertFrom-Json).Config.Labels | Format-List
```

**Spoken script (as in the video):**

> The image carries its own identity. I inspect the image from the registry tag and print its labels. The revision label holds the commit id, and the version label the version. These labels are written at build time from the build arguments. So even without Jenkins, anyone can ask an image which commit it was built from.

**What the output means:** org.opencontainers.image.revision = the commit (1c2103c), org.opencontainers.image.version = 1.1.0, title hotel-booking-app.

**What I will tell the professor:** "Each image carries the commit and version it was built from, as labels."

## Step 6 - Deployment: a fresh container [video 02:36]

**What I am doing:** running

```powershell
(Invoke-WebRequest 'http://localhost:8090/job/hotel-booking/lastBuild/consoleText' -Headers $jh -UseBasicParsing).Content -split '\r?\n' | Select-String 'docker compose (pull|up)|Container hotel-staging-app-1 (Recreate|Started|Healthy)|Deployed ' | ForEach-Object { $_.Line -replace '^\[[^\]]+\]\s*', '' }
```

**Spoken script (as in the video):**

> Deployment. Jenkins runs docker compose pull, which fetches the images that were just published, then docker compose up with the wait option. Look at the log: the staging app container was recreated, started, and Docker reported it healthy, then the Nginx container as well. It was recreated because the new image has a new identity. The database stays safe, because it lives in a separate volume.

**What the output means:** '+ docker compose pull', '+ docker compose up -d --no-build --wait ...', 'Container hotel-staging-app-1 Recreated / Started / Healthy' and 'Deployed 1.1.0-... to staging: http://localhost:8081'.

**What I will tell the professor:** "The pipeline pulled the tested image and started a fresh container, waiting until it was healthy."

## Step 7 - The running container is the published image [video 03:09]

**What I am doing:** running

```powershell
docker ps --filter name=hotel-staging --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'; 'running container image id: ' + (docker inspect hotel-staging-app-1 --format '{{.Image}}'); 'registry tag image id     : ' + (docker image inspect "localhost:5000/hotel-booking-app:$tag" --format '{{.Id}}')
```

**Spoken script (as in the video):**

> Is the container running the image that was tested and published? I compare two image ids. The first is the image the running staging container was created from. The second is the image behind the tag in the registry. They are identical, character for character. The tested image became the deployed release, with no rebuild in between. The container list shows both staging containers, healthy.

**What the output means:** hotel-staging-app-1 and hotel-staging-nginx-1 Up (healthy), staging port 8081, and two identical sha256 image ids.

**What I will tell the professor:** "The container runs exactly the image that Jenkins tested and published."

## Step 8 - Health verification: version and commit [video 03:41]

**What I am doing:** running

```powershell
curl.exe -s http://localhost:8081/health; ''; 'commit at the tip of develop: ' + (git rev-parse --short develop); 'health.json saved by Jenkins:'; Invoke-RestMethod 'http://localhost:8090/job/hotel-booking/lastBuild/artifact/reports/health.json' -Headers $jh | ConvertTo-Json -Compress
```

**Spoken script (as in the video):**

> Finally the health verification. I ask the running staging application for its health: status ok, environment staging, the version, and the commit. I compare the commit with the tip of develop, and with the health file that the pipeline itself saved during its health check stage. All the same. The deployed version is traceable to one commit and one Jenkins build.

**What the output means:** {"commit":"1c2103c","env":"staging","status":"ok","version":"1.1.0"}, the same commit as develop, and the same JSON in health.json.

**What I will tell the professor:** "The deployed version and commit match the build, so the release is verified and traceable."

## Step 9 - Docker Hub: the honest status [video 04:11]

**What I am doing:** running

```powershell
Select-String -Path Jenkinsfile -Pattern 'startsWith|registry-creds|docker login|name: .REGISTRY' | ForEach-Object { '{0,3}: {1}' -f $_.LineNumber, $_.Line.Trim() }
```

**Spoken script (as in the video):**

> I must be honest about Docker Hub. The pipeline supports it: if the registry parameter does not start with localhost, it logs in with a Jenkins credential called registry creds, and the password is masked in the log. These are the lines. But I never ran it, because it needs a Docker Hub account and an access token. Everything shown in this video used the local registry. To publish externally I would set the registry parameter to docker dot io slash my id and add the credential in Jenkins. I will not publish anything or store credentials without your authorization.

**What the output means:** The REGISTRY parameter, the startsWith('localhost') test, withCredentials registry-creds and the docker login line.

**What I will tell the professor:** "Docker Hub publishing is implemented but untested; the local registry was used and verified."
