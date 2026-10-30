# Task 8 - narration script

**Task 8 - Pipeline as Code and Server Deployment**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

# Part: Task 8 (part 1) - Pipeline as code: the Jenkinsfile, stage by stage

## Step 1 - The Jenkinsfile and the quality gate [video 00:01]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -First 16
```

**Spoken script (as in the video):**

> This is Task 8, pipeline as code and deployment. A Jenkinsfile describes the whole build and deployment process as code, stored in the repository next to the application. This is the top of ours. The comment shows the flow: checkout, install, static checks, tests, Selenium, package, build images, publish, deploy and health check. And the key rule, the quality gate: if any command fails, its stage fails and every later stage is skipped.

**What the output means:** The header comment with the stage flow and the quality gate explanation, plus the agent and credentials requirements.

**What I will tell the professor:** "The pipeline is code in Git, and any failure stops everything after it, including deployment."

## Step 2 - Parameters and the polling trigger [video 00:39]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 18 -First 18
```

**Spoken script (as in the video):**

> These are the pipeline parameters. They configure the target environment without changing the code. APP ENV chooses staging or prod. BRANCH chooses which Git branch to build. REGISTRY chooses where images are published, by default the local registry. Below is the trigger: poll SCM every five minutes. A GitHub webhook would be faster, but GitHub cannot reach a Jenkins running on localhost, so Jenkins asks Git for new commits instead.

**What the output means:** parameters { choice APP_ENV [staging, prod]; string BRANCH develop; string REGISTRY localhost:5000 } and triggers { pollSCM('H/5 * * * *') }.

**What I will tell the professor:** "Parameters choose the environment, and polling gives continuous integration without a public server."

## Step 3 - Options and environment variables [video 01:15]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 37 -First 15
```

**Spoken script (as in the video):**

> Options: timestamps in the log, only the last twenty builds are kept, no two builds run at the same time because two deployments would fight over the same containers, and a thirty minute time limit. Environment variables: the Python version, and the host port, which is 8082 for prod and 8081 for staging, decided by the parameter. The compose project name includes the environment, so staging and prod get separate containers and separate database volumes.

**What the output means:** options { timestamps, buildDiscarder 20, disableConcurrentBuilds, timeout 30 min } and environment { PYTHON, HOST_PORT staging 8081 / prod 8082, COMPOSE_PROJECT_NAME hotel-<env> }.

**What I will tell the professor:** "The environment parameter decides the port and a separate set of containers and data."

## Step 4 - Stage 1: Checkout [video 01:52]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 54 -First 21
```

**Spoken script (as in the video):**

> Stage one, checkout. Jenkins gets the source from Git. The next line deletes the reports and dist folders from the previous build, because the workspace is reused, and an old test report must never be published as the result of the new build. Then it builds the version: the VERSION file plus the short commit id, for example 1.1.0 dash 1c2103c. That one tag is used for the source archive, both images and the health check, so every deployment traces back to one commit.

**What the output means:** checkout scm, 'rm -rf reports dist', APP_VERSION from the VERSION file, GIT_SHORT, IMAGE_TAG = version-commit, build display name.

**What I will tell the professor:** "Checkout fetches the commit, clears old reports and computes the version-and-commit tag."

## Step 5 - Stages 2 and 3: install and static checks [video 02:31]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 75 -First 23
```

**Spoken script (as in the video):**

> Stage two installs dependencies. It creates a fresh Python virtual environment and installs the pinned requirements, so the build is reproducible. Stage three, static checks, runs compile all, which finds syntax errors, and flake8, which finds style problems, unused imports and undefined names. These are the build and lint steps for a Python project, and the equivalent of compile in Java. This is not a Maven build.

**What the output means:** Install: python3.11 -m venv, pip install -r requirements-dev.txt. Static checks: compileall and flake8.

**What I will tell the professor:** "Dependencies are installed in a clean environment and the code is syntax- and style-checked before any test."

## Step 6 - Stages 4 and 5: the tests, the quality gate [video 03:06]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 98 -First 14
```

**Spoken script (as in the video):**

> Stage four runs the unit and integration tests with pytest and writes a JUnit XML report. Stage five runs the Selenium browser tests in headless Chromium. Each is just a shell command. If pytest finds a failing test, it exits with an error code, the stage turns red, and Jenkins skips everything after it: packaging, images, publishing and deployment. That is the quality gate, and it is why untested code can never be deployed.

**What the output means:** 'pytest tests/unit tests/integration --junitxml=reports/unit-integration-tests.xml' and 'pytest -m e2e --junitxml=reports/e2e-tests.xml'.

**What I will tell the professor:** "A failing test stops the pipeline before anything is packaged or deployed."

## Step 7 - Stage 6: package the source with a checksum [video 03:41]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 112 -First 14
```

**Spoken script (as in the video):**

> Stage six packages the source. Git archive creates a tar gz file with exactly the committed files of this commit, nothing uncommitted. Then sha256 sum writes a checksum file next to it, so anyone can verify later that the archive is unchanged. Both files are archived with the build. This is the source artifact of our pipeline.

**What the output means:** git archive ... hotel-booking-$IMAGE_TAG.tar.gz and sha256sum written to a .sha256 file.

**What I will tell the professor:** "Every build produces a source archive and a checksum that identify exactly what was built."

## Step 8 - Stage 7: build the Docker images [video 04:09]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 126 -First 14
```

**Spoken script (as in the video):**

> Stage seven builds two Docker images, the application and the Nginx proxy. Both are tagged with the registry prefix and the version and commit tag. The application image receives the version and the commit as build arguments, so the running container can report them on the health address.

**What the output means:** docker build -t ${IMAGE_PREFIX}hotel-booking-app:$IMAGE_TAG with --build-arg APP_VERSION and GIT_COMMIT, and the nginx image.

**What I will tell the professor:** "The images are tagged with version and commit so each one is traceable."

## Step 9 - Stage 8: publish the images to the registry [video 04:31]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 140 -First 22
```

**Spoken script (as in the video):**

> Stage eight publishes the images. With the local registry, localhost colon 5000, a simple docker push is enough. For a remote registry such as Docker Hub, the pipeline uses a Jenkins credential, and the password is masked in the log. I must be honest: only the local registry was tested. Docker Hub is supported by the code but was never run, because it needs an account and a credential.

**What the output means:** docker push for app and nginx; if the registry starts with localhost no login, else withCredentials registry-creds and docker login.

**What I will tell the professor:** "Images go to a local registry; the Docker Hub path exists in the code but was not tested."

## Step 10 - Stage 9: deploy [video 05:04]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 162 -First 14
```

**Spoken script (as in the video):**

> Stage nine deploys. The secret key is injected from a Jenkins credential, only for this block, and masked in the log. Docker compose pull fetches exactly the images that were just published. Docker compose up with dash dash wait starts the containers and blocks until they are healthy. If they never become healthy within two minutes, the stage fails. Deployment uses the tested image, never a rebuild.

**What the output means:** withCredentials hotel-secret-key; docker compose pull; docker compose up -d --no-build --wait --wait-timeout 120.

**What I will tell the professor:** "Deploy pulls the exact tested images and waits until they are healthy."

## Step 11 - Stage 10: health check and version verification [video 05:36]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 176 -First 17
```

**Spoken script (as in the video):**

> Stage ten, the health check. It calls the health address through the whole chain, Nginx, Gunicorn and SQLite, and saves the answer. Then two grep commands check that the version and the commit reported by the running application are exactly the ones this build created. If a wrong version were running, this stage would fail. This is how we know that what is deployed is what was tested.

**What the output means:** wget /health inside the nginx container, saved to reports/health.json, then grep for the exact version and commit.

**What I will tell the professor:** "The pipeline verifies that the running version and commit are the ones it just built."

## Step 12 - The deployment record and post actions [video 06:06]

**What I am doing:** running

```powershell
Get-Content Jenkinsfile | Select-Object -Skip 193 -First 28
```

**Spoken script (as in the video):**

> Finally, a deployment record is written: environment, branch, version, commit, image names, the address and the Jenkins build address. After every build, success or failure, the post section publishes the test results and archives reports, failure screenshots, the source archive and the record. Jenkins then shows pass and fail trends. A failure message says that nothing was deployed.

**What the output means:** reports/deployment.txt content, then post { always { junit + archiveArtifacts }, success { echo Deployed ... }, failure { echo FAILED - nothing was deployed } }.

**What I will tell the professor:** "Every build leaves a test report, artifacts and a deployment record behind."

## Step 13 - The stage order is the quality gate [video 06:39]

**What I am doing:** running

```powershell
Select-String -Path Jenkinsfile -Pattern "stage\('" | ForEach-Object { '{0,3}: {1}' -f $_.LineNumber, $_.Line.Trim() }
```

**Spoken script (as in the video):**

> To summarise, here are the stages with their line numbers. The tests come before package, images, publish and deploy. Deployment happens only after the quality gates pass. The next part of this video shows a real run of this pipeline in Jenkins.

**What the output means:** Ten stages: Checkout, Install dependencies, Static checks, Unit & integration tests, E2E tests (Selenium), Package source, Build images, Publish images, Deploy, Health check.

**What I will tell the professor:** "Deployment can only happen after every earlier stage has passed."

# Part: Task 8 (part 2) - A live pipeline run in Jenkins: source to deployed staging

## Step 14 - Start a real build: Build with Parameters [video 07:03]

**Spoken script (as in the video):**

> Now a real run. In Jenkins I choose Build with Parameters. The form shows the three parameters of the Jenkinsfile with their defaults: APP ENV staging, so it deploys to the staging environment on port eight thousand eighty one; BRANCH develop, the integration branch; and REGISTRY localhost colon five thousand, the local registry. I click Build.

**What the output means:** The parameter form with APP_ENV staging, BRANCH develop, REGISTRY localhost:5000; after clicking Build a new build is queued.

**What I will tell the professor:** "I start a real build of develop and deploy it to staging, using the parameters of the Jenkinsfile."

## Step 15 - Watching the stages: checkout, install, static checks, tests [video 07:28]

**Spoken script (as in the video):**

> This is the stage view of the new build, filling in live. Stage one, checkout, fetches the commit and builds the version and commit tag. Stage two installs the dependencies in a fresh virtual environment. Stage three, static checks, compiles the code and runs the linter. Stage four runs the unit and integration tests. If any of these turns red, everything after it is skipped.

**What the output means:** A new row at the top of the Stage View whose cells turn green one after another.

**What I will tell the professor:** "The pipeline runs checkout, install, static checks and the tests, and stops at the first failure."

## Step 16 - Watching the stages: Selenium, package, images, registry [video 07:56]

**Spoken script (as in the video):**

> Stage five runs the Selenium browser tests in headless Chromium, about twenty seconds. Stage six packages the source archive and writes its checksum. Stage seven builds the two Docker images, the application and Nginx, tagged with the version and the commit. Stage eight publishes both images to the local registry. Only code that passed every test gets this far.

**What the output means:** The row continues turning green: E2E tests, Package source, Build images, Publish images.

**What I will tell the professor:** "Images are built and published only after all the tests pass."

## Step 17 - Deploy and health check, then the result [video 08:25]

**Spoken script (as in the video):**

> Stage nine deploys: Docker compose pulls the published images and starts the containers, and waits until they are healthy. Stage ten, the health check, asks the running application for its version and commit and compares them with this build. When the whole row is green, the build is a success. I wait for the build to finish.

**What the output means:** The row is fully green and the new build is marked SUCCESS in the build history.

**What I will tell the professor:** "The build finished green: tested, packaged, published, deployed and verified."

## Step 18 - The console: images, registry push, deployment [video 08:48]

**Spoken script (as in the video):**

> The console of the new build confirms each step. Docker build created the application image, tagged with the registry, the version and the commit. Docker push published it. Docker compose up with the wait option started the containers, and Docker reported them healthy. Finally the pipeline printed deployed, with the version, commit tag and the staging address.

**What the output means:** Highlighted: the docker build command with the registry tag, docker push, compose up --wait and the final 'Deployed ... to staging: http://localhost:8081'.

**What I will tell the professor:** "The log shows the image built, pushed to the registry, deployed and reported healthy."

## Step 19 - The deployment record [video 09:14]

**Spoken script (as in the video):**

> Every deployment writes a record, archived with the build. It says the environment, the branch, the version, the commit, the image tag, the names of both images, the address, and the Jenkins build address. This is the traceability: from a running staging container back to one commit and one build.

**What the output means:** Plain text: environment=staging, branch=develop, version=1.1.0, commit=<short sha>, image_tag, app_image, nginx_image, url=http://localhost:8081, jenkins_build=...

**What I will tell the professor:** "Each deployment leaves a record that traces the running version back to a commit and a build."
