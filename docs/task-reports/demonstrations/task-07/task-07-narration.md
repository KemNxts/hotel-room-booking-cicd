# Task 7 - narration script

**Task 7 - Jenkins Installation and Continuous Integration**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

# Part: Task 7 (part 1) - Jenkins installation and what is really set up (terminal)

## Step 1 - Jenkins as a container: the compose file [video 00:01]

**What I am doing:** running

```powershell
Get-Content deploy/jenkins/docker-compose.yml | Select-String -NotMatch '^\s*#' | Select-String 'image:|ports:|8090|5000|jenkins-home|docker.sock|/repo|restart:|registry' | ForEach-Object { $_.Line.Trim() }
```

**Spoken script (as in the video):**

> This is Task 7, Jenkins installation and continuous integration. Jenkins is an automation server. It watches the repository, and for every change it runs the build and the tests automatically, so that mistakes are found in minutes, not weeks. This is continuous integration. Here Jenkins runs as a Docker container. These lines of its compose file show the setup: the port 8090, only reachable from this computer, a named volume that keeps jobs and builds, the Docker socket so Jenkins can build images, our repository mounted read only, and a local image registry on port 5000.

**What the output means:** The jenkins image, 127.0.0.1:8090:8080, the registry on 5000, the jenkins-home volume, docker.sock, ../..:/repo:ro and restart: unless-stopped.

**What I will tell the professor:** "Jenkins runs as a reproducible container with its data in a volume and the project mounted read-only."

## Step 2 - What is inside the Jenkins image [video 00:47]

**What I am doing:** running

```powershell
Get-Content deploy/jenkins/Dockerfile | Select-String -NotMatch '^\s*#' | Select-String 'FROM|python3.11|chromium|docker:|plugin' | ForEach-Object { $_.Line.Trim() }; '--- plugins.txt'; Get-Content deploy/jenkins/plugins.txt
```

**Spoken script (as in the video):**

> The Jenkins image is built from our own Dockerfile. It starts from the official long term support Jenkins, and adds what our pipeline needs: Python three point eleven, the same version as production, Chromium and chromedriver for the Selenium tests, and the Docker command line tool. The plugins list is short: pipeline, Git, JUnit for test reports, credentials binding, the stage view, and timestamps.

**What the output means:** FROM jenkins/jenkins:lts-jdk21, Python 3.11 copied in, chromium and chromium-driver, the Docker CLI, then the six plugins.

**What I will tell the professor:** "The Jenkins image contains Python, Chromium and the Docker CLI, so the whole pipeline can run inside it."

## Step 3 - Start-up and the running instance [video 01:20]

**What I am doing:** running

```powershell
Select-String -Path docs/05-ci-cd-pipeline.md -Pattern 'docker compose up' | Select-Object -First 1 | ForEach-Object { $_.Line }; docker ps --filter name=hotel-jenkins --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'; 'Jenkins version: ' + (Invoke-WebRequest http://localhost:8090/login -UseBasicParsing).Headers['X-Jenkins']
```

**Spoken script (as in the video):**

> To start Jenkins, the documented procedure is docker compose up dash d, in the deploy slash jenkins folder, then wait about a minute. Now I check that it is really running: both containers are up, and the login page answers with the Jenkins version in its response header. If Jenkins were stopped, this is the command I would run.

**What the output means:** The documented command, two containers hotel-jenkins-jenkins-1 and hotel-jenkins-registry-1 'Up', and 'Jenkins version: 2.580.1'.

**What I will tell the professor:** "Jenkins and the registry are running, and the start-up command is documented."

## Step 4 - Level 1: the Jenkinsfile exists in Git [video 01:47]

**What I am doing:** running

```powershell
git ls-files Jenkinsfile; git log --oneline -4 -- Jenkinsfile
```

**Spoken script (as in the video):**

> Now an important distinction. Three different things can be true. First: a Jenkinsfile exists in the repository. That is only a file. Git ls files proves it is tracked, and the log shows who changed it and why. But a file alone runs nothing.

**What the output means:** 'Jenkinsfile' is tracked, followed by its last four commits.

**What I will tell the professor:** "A Jenkinsfile in Git is only the recipe; it does not prove that Jenkins ever ran it."

## Step 5 - Level 2: the Jenkins job is configured [video 02:09]

**What I am doing:** running

```powershell
$jh = @{ Authorization = 'Basic ' + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes('admin:' + ((Get-Content deploy/jenkins/.env | Where-Object { $_ -like 'JENKINS_ADMIN_PASSWORD=*' }) -replace '^[^=]+=', ''))) }; (Invoke-WebRequest 'http://localhost:8090/job/hotel-booking/config.xml' -Headers $jh -UseBasicParsing).Content -split '\r?\n' | Select-String 'url>|name>\*|scriptPath|<spec>|<name>(APP_ENV|BRANCH|REGISTRY)' | ForEach-Object { $_.Line.Trim() }
```

**Spoken script (as in the video):**

> Second: a job is configured in Jenkins. I ask Jenkins for the job configuration, using the admin password that the command reads from the environment file, without displaying it. The configuration says: poll the Git repository every five minutes, take the branch from the BRANCH parameter, read the pipeline from the file called Jenkinsfile, and the repository is the mounted project. The job has three parameters.

**What the output means:** <spec>H/5 * * * *</spec>, the parameter names APP_ENV, BRANCH, REGISTRY, <url>file:///repo</url>, <name>*/${BRANCH}</name> and <scriptPath>Jenkinsfile</scriptPath>.

**What I will tell the professor:** "The job is configured to poll the repository, pick the branch from a parameter and run the Jenkinsfile."

## Step 6 - Level 3: the job actually ran, and what happened [video 02:43]

**What I am doing:** running

```powershell
Invoke-RestMethod 'http://localhost:8090/job/hotel-booking/api/json?tree=builds[number,result,displayName]' -Headers $jh | Select-Object -ExpandProperty builds | Format-Table number, result, displayName -AutoSize
```

**Spoken script (as in the video):**

> Third, and the only one that proves anything: the job actually ran. This is the real build history from Jenkins. Eleven builds. Most are success. Builds two and nine are failures: those are the deliberate defect experiments of Task 10. Build eleven, the most recent, succeeded. The names show the version and the commit that each build used.

**What the output means:** Builds #1 to #11 with their result: SUCCESS for most, FAILURE for #2 and #9, each named version-commit.

**What I will tell the professor:** "A job that is configured is not enough; the build history shows it really ran, with passes and deliberate failures."

## Step 7 - The stages of build 11 [video 03:14]

**What I am doing:** running

```powershell
(Invoke-RestMethod 'http://localhost:8090/job/hotel-booking/11/wfapi/describe' -Headers $jh).stages | Select-Object name, status, @{ n = 'seconds'; e = { [int]($_.durationMillis / 1000) } } | Format-Table -AutoSize
```

**Spoken script (as in the video):**

> Here are the stages of build eleven, with the status and the time of each. Checkout, install dependencies, static checks, which is the linting, unit and integration tests, the Selenium tests, packaging the source, building the images, publishing, deploying and the health check. All success. The whole pipeline took about one hundred and three seconds. Note: this build is from the twentieth of October. It is real, but it is a historic build, not one I started just now.

**What the output means:** Eleven stages, each SUCCESS, e.g. Unit & integration tests 19s, E2E tests 20s, Build images 15s, Deploy 12s.

**What I will tell the professor:** "Every stage of build 11 passed; it is a real historic build from 20 October."

## Step 8 - Proof in the log: install, lint, tests, packaging [video 03:54]

**What I am doing:** running

```powershell
(Invoke-WebRequest 'http://localhost:8090/job/hotel-booking/11/consoleText' -Headers $jh -UseBasicParsing).Content -split '\r?\n' | Select-String 'Building commit|Python 3|pip install|flake8|passed|sha256sum hotel|Finished:' | ForEach-Object { $_.Line.Trim() -replace '^\[[^\]]+\]\s*', '' }
```

**Spoken script (as in the video):**

> Finally, evidence from the console log of build eleven. Pip install runs for the dependencies. Flake8 is the linter. Eighty five unit and integration tests passed. Five Selenium tests passed, and the other eighty five were deselected, as intended. Then the checksum of the source archive is created, and the build finishes with SUCCESS. If a stage had failed, this is where the failure would be.

**What the output means:** Building commit 1c2103c on develop, Python 3.11, pip install, flake8, '85 passed', '5 passed, 85 deselected', sha256sum, Finished: SUCCESS.

**What I will tell the professor:** "The console log shows dependency installation, linting, the tests and the checksum, ending in SUCCESS."

# Part: Task 7 (part 2) - The Jenkins web interface: job, configuration, build, console, tests, artifacts

## Step 9 - The Jenkins dashboard [video 04:31]

**Spoken script (as in the video):**

> Now the Jenkins web interface, version two point five eight, open on localhost port eight thousand ninety, already logged in as admin. This is the dashboard. It lists the jobs. We have one, called hotel booking, which is the continuous integration job for our project. The little weather icon and the last success and last failure columns summarise its health.

**What the output means:** The Jenkins dashboard listing the job hotel-booking with its last success and last failure.

**What I will tell the professor:** "This is the real Jenkins, with our CI job."

## Step 10 - The job page: stage view and build history [video 04:57]

**Spoken script (as in the video):**

> The job page. On the left is the build history, the newest first. In the middle, the stage view draws every build as a row and every pipeline stage as a column. Green is success. The red cells in build number two and nine are the deliberate failures. The test result trend shows the number of passed tests growing as the project grew.

**What the output means:** The Stage View table with eleven builds and the Test Result Trend graph.

**What I will tell the professor:** "The stage view shows every build and exactly which stage passed or failed."

## Step 11 - The job configuration: parameters, polling, Git [video 05:22]

**Spoken script (as in the video):**

> The job configuration, opened read only. I will not save anything. First: this project is parameterized, with APP ENV, BRANCH and REGISTRY. Then build triggers: Poll SCM, every five minutes, which makes Jenkins check Git for new commits. This is the continuous integration trigger. Then the pipeline: the definition is Pipeline script from SCM, the repository URL, the branch specifier, which uses the BRANCH parameter, and the script path, Jenkinsfile.

**What the output means:** The parameterized checkbox with three parameters, Poll SCM with H/5 * * * *, Repository URL file:///repo, Branch Specifier */${BRANCH}, Script Path Jenkinsfile.

**What I will tell the professor:** "The job polls Git every five minutes, picks the branch from a parameter, and reads the pipeline from the Jenkinsfile."

## Step 12 - One real build: number 11 [video 05:59]

**Spoken script (as in the video):**

> Now one real build, number eleven, from the twentieth of October. It was started with the parameters staging, branch develop and the local registry. Its name, one point one point zero, dash one c two one zero three c, is the version and the commit. The page shows the status, the duration, and the links to the console output, the test result, and the artifacts.

**What the output means:** Build #11 page: success icon, the version-commit name, links to Console Output, Test Result and the build artifacts.

**What I will tell the professor:** "Build 11 is a real, successful build with a version and commit in its name."

## Step 13 - The console output: install, lint, test [video 06:27]

**Spoken script (as in the video):**

> The console output is the complete log. First the commit being built. Then the dependencies are installed with pip, from the pinned requirements. Then flake8, the linter, runs and finds nothing, so it prints nothing. Then eighty five unit and integration tests pass. Then five Selenium tests pass, and the rest are deselected. The log ends with finished, success.

**What the output means:** Highlighted lines: Building commit 1c2103c, the pip install command, the flake8 command, '85 passed', '5 passed, 85 deselected' and 'Finished: SUCCESS'.

**What I will tell the professor:** "The console log proves the dependencies were installed, the code was linted and all tests passed."

## Step 14 - Test results and reports [video 06:56]

**Spoken script (as in the video):**

> Jenkins also reads the JUnit XML reports and shows them as a test result page. Here are the two test suites, with the number of tests, failures and the duration of each. Because the reports are published after every build, Jenkins can draw the trend we saw before, and a failing test appears here by name.

**What the output means:** The Test Result summary with 0 failures and the list of packages / test suites.

**What I will tell the professor:** "Jenkins publishes the test reports, so every build has a visible test result."

## Step 15 - Archived artifacts: source archive and checksum [video 07:18]

**Spoken script (as in the video):**

> Every build archives its artifacts. In the dist folder: the source archive, a tar gz file named with the version and commit, and its sha two five six checksum. In the reports folder: the test reports, the health check answer and the deployment record. They are kept with the build, so any build can be reproduced or checked later.

**What the output means:** The artifact folders dist and reports; inside dist the tar.gz and the .sha256 file.

**What I will tell the professor:** "Each build archives its source package with a checksum and its reports."

## Step 16 - Build history and the pass/fail trend [video 07:43]

**Spoken script (as in the video):**

> Back on the job page: the build history and the trend. Jenkins keeps the last twenty builds. Over the project, the number of passing tests grew, and the failures are the two deliberate experiments. This is continuous integration at work: every change is built and tested, and the result is visible to everyone.

**What the output means:** The job page with the build list on the left and the trend graph.

**What I will tell the professor:** "Every change gets built and tested, and the history of passes and failures is visible."
