# Task 10 - narration script

**Task 10 - Continuous Testing in Jenkins**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

# Part: Task 10 (part 1) - The defect experiment: code, a live failing test, and the stale-report fix

## Step 1 - How a failing test stops the pipeline [video 00:01]

**What I am doing:** running

```powershell
Select-String -Path Jenkinsfile -Pattern "stage\('|pytest|junit |rm -rf reports" | ForEach-Object { '{0,3}: {1}' -f $_.LineNumber, $_.Line.Trim() }
```

**Spoken script (as in the video):**

> This is Task 10, continuous testing in Jenkins. The idea is simple. Each test stage runs a command. When pytest finds a failing test, it exits with a non zero code, Jenkins marks the stage failed, and every later stage is skipped. These are the lines of the Jenkinsfile that do it: the two test commands, the report publishing that always runs, and the clean up line at the start. Notice that package, images, publish and deploy come after the tests.

**What the output means:** Stage names with line numbers, the two pytest commands (unit/integration and e2e), 'rm -rf reports dist' in Checkout, and the junit step in post.

**What I will tell the professor:** "A failing pytest command turns the stage red and Jenkins skips everything after it, including deployment."

## Step 2 - The experiment branch: a deliberate defect [video 00:39]

**What I am doing:** running

```powershell
git log --oneline develop..experiment/defect-demo; 'branches that contain the defect commit:'; git branch --contains 5844eec
```

**Spoken script (as in the video):**

> To prove the quality gate, I introduced a deliberate defect on a throw away branch called experiment slash defect demo. It has two commits: first the defect, then the corrective fix. And this second command proves the safety: it lists the branches that contain the defect commit. Only the two experiment branches. The defect was never merged into develop or main.

**What the output means:** Two commits (the experiment commit and the fix) and only experiment/defect-demo and experiment/defect-demo-2 containing the defect.

**What I will tell the professor:** "The defect exists only on throw-away experiment branches and was never merged."

## Step 3 - The defect: one character [video 01:07]

**What I am doing:** running

```powershell
git diff 5844eec^ 5844eec -- app/dao/booking_dao.py
```

**Spoken script (as in the video):**

> This is the defect. In the overlap rule of the booking data access layer, the strict comparison, check in less than check out, became less than or equal. A tiny off by one change, but it wrongly says that a room is booked when one guest checks out on the same day another checks in. A subtle bug like this is exactly what automated tests exist to catch.

**What the output means:** A one-line diff: '-    check_in < :check_out' and '+    check_in <= :check_out' in _OVERLAP_SQL.

**What I will tell the professor:** "The injected defect is a one-character off-by-one change in the overlap rule."

## Step 4 - Live: the tests catch the defect [video 01:35]

**What I am doing:** running

```powershell
$d = "$env:TEMP/defect-demo"; Remove-Item $d -Recurse -Force -ErrorAction SilentlyContinue; git clone -q . $d; git -C $d checkout -q 5844eec; Push-Location $d; python -m pytest tests/unit tests/integration -q -p no:cacheprovider 2>&1 | Select-Object -Last 6; 'pytest exit code: ' + $LASTEXITCODE; Pop-Location
```

**Spoken script (as in the video):**

> Now I reproduce what Jenkins saw, safely. I clone the repository into a disposable folder, check out the defect commit, and run the same tests the pipeline runs. A test fails, the summary says failed, and the exit code is one. That non zero code is exactly what makes Jenkins stop. Nothing in my real project changed.

**What the output means:** FAILED ...test_overlap_rules[...] near the end, '1 failed, ... passed' (or similar) and 'pytest exit code: 1'.

**What I will tell the professor:** "With the defect, pytest fails and returns exit code 1, which is what stops the Jenkins pipeline."

## Step 5 - Live: the corrective commit makes it green [video 02:09]

**What I am doing:** running

```powershell
git -C $d checkout -q 2fb62d6; Push-Location $d; python -m pytest tests/unit tests/integration -q -p no:cacheprovider 2>&1 | Select-Object -Last 3; 'pytest exit code: ' + $LASTEXITCODE; Pop-Location; git show 2fb62d6 --format='%h %s' -- app/dao/booking_dao.py | Select-Object -First 12
```

**Spoken script (as in the video):**

> Now the corrective commit. I check out the fix in the same disposable clone and run the same tests. They all pass, and the exit code is zero. In Jenkins, this is build number three: green, and the deployment stage runs. The fix restored the strict comparison, one line in one file.

**What the output means:** '82 passed' (the unit and integration tests that existed at that commit; Jenkins added the 5 browser tests for 87), exit code 0, then the one-line fix diff restoring '<'.

**What I will tell the professor:** "The corrective commit makes every test pass again, so the next pipeline run goes green and deploys."

## Step 6 - Clean up the disposable clone [video 02:38]

**What I am doing:** running

```powershell
Remove-Item $d -Recurse -Force; 'clone exists: ' + (Test-Path $d); git status --short --branch
```

**Spoken script (as in the video):**

> I delete the disposable clone and confirm that my project is untouched: same branch, and no new changes except this demonstration folder.

**What the output means:** 'clone exists: False' and the project's own branch with only the untracked demonstrations folder.

**What I will tell the professor:** "The defect never touched my project; it only existed in a throw-away clone and on experiment branches."

## Step 7 - The stale test report bug and its fix [video 02:51]

**What I am doing:** running

```powershell
git show 32d5f8e --format='%h %s' -U1 -- Jenkinsfile | Select-Object -First 16
```

**Spoken script (as in the video):**

> Studying build two, I found a real problem. Its test report listed five Selenium tests as passed, although the Selenium stage had been skipped. Jenkins reuses its workspace, so the old report from build one was still there and was published again. The fix, on branch fix slash jenkins stale reports, is this: the checkout stage now deletes the reports and dist folders first. A build can no longer publish a report from an older build.

**What the output means:** The commit 'fix: stop Jenkins publishing stale test reports from earlier builds' adding the comment lines and sh 'rm -rf reports dist' to the Checkout stage.

**What I will tell the professor:** "Every build now starts by deleting old reports, so a stale report can never be mistaken for a new one."

## Step 8 - Commit IDs in the Jenkins evidence [video 03:27]

**What I am doing:** running

```powershell
Select-String -Path docs/evidence/git/commit-id-map.md -Pattern '554cad3|30c6a05|8505486' | ForEach-Object { $_.Line }
```

**Spoken script (as in the video):**

> One last detail you may be asked about. The Jenkins builds were made before the history was rewritten, so Jenkins and the evidence logs show the original commit IDs. This map links each original ID to the current one: the defect commit, the corrective fix, and the stale report fix are all listed, with the same subject lines. Same changes, new hash.

**What the output means:** Table rows mapping 554cad3 -> 5844eec, 30c6a05 -> 2fb62d6 and 8505486 -> a3d8626 with their subjects.

**What I will tell the professor:** "The evidence cites the original commit IDs; the map shows the current ones."

# Part: Task 10 (part 2) - The defect experiment in Jenkins: real builds #1, #2, #3, #9 and #11

## Step 9 - The Stage View: build 2 is red [video 03:59]

**Spoken script (as in the video):**

> This is the job's stage view, and the real defect experiment. The rows are builds. Build number one is green: the baseline, version one point zero point zero, commit six four three five one f e. Build number two, the one with the deliberate defect, is red, and it fails at exactly one place: the unit and integration tests stage. Build number three is green again.

**What the output means:** The Stage View where the row of build #2 has a red cell under 'Unit & integration tests' and later cells also red.

**What I will tell the professor:** "The defect build failed in the unit test stage, and the build after the fix is green again."

## Step 10 - Build 2: the console shows the failing test [video 04:26]

**Spoken script (as in the video):**

> Build two's console. Pytest reports one failed, eighty one passed. The failure has a name: test overlap rules, with the dates the eighth to the tenth of January 2030. The assertion says room one oh one was expected to be free, but it was reported booked. That is exactly the off by one defect.

**What the output means:** Highlighted: the FAILED line naming test_overlap_rules and the summary '1 failed, 81 passed'.

**What I will tell the professor:** "Jenkins names the exact test that caught the defect."

## Step 11 - Why deployment was skipped [video 04:49]

**Spoken script (as in the video):**

> And here is the quality gate. Right after the failure, for every following stage Jenkins writes: stage skipped due to earlier failures. E2E tests, package source, build images, publish images, and deploy. Nothing was packaged, nothing was published, and nothing was deployed. The pipeline ends with its own message: pipeline failed, nothing was deployed.

**What the output means:** Highlighted: 'Stage ... skipped due to earlier failure(s)' lines and 'Pipeline FAILED ... Nothing was deployed.'

**What I will tell the professor:** "After the failed tests every later stage was skipped, so nothing was deployed."

## Step 12 - The Test Result page of build 2 [video 05:17]

**Spoken script (as in the video):**

> The test result page of build two lists the failing test by name, with its error. This page also contains something surprising, which I will explain in a moment: a package called tests dot e2e with five passed tests, although the Selenium stage never ran in this build.

**What the output means:** Test Result with 1 failure and the package list including tests.e2e (5 tests, all passed).

**What I will tell the professor:** "The report shows the failing test, and also revealed a stale-report problem."

## Step 13 - The stale report problem, proved by the artifacts [video 05:36]

**Spoken script (as in the video):**

> This is the stale report bug. Build two never packaged anything, yet its artifacts list a source archive and a deployment record. They are not new. They are left over from build number one, because Jenkins reuses its workspace, and the archive step collected the old files. That is why build two showed five passing Selenium tests: they came from build one's report.

**What the output means:** The artifact folder of build #2 listing dist/hotel-booking-1.0.0-64351fe.tar.gz: the version and commit of build #1, not of build #2.

**What I will tell the professor:** "Build 2 published old files from build 1, which is the stale artifact bug that I then fixed."

## Step 14 - Staging before the defect: the record of build 1 [video 06:02]

**Spoken script (as in the video):**

> What happened to staging? The deployment record of build one says staging ran version one point zero point zero, commit six four three five one f e. Because build two's deploy stage was skipped, the staging containers were never touched. So that version stayed active the whole time the defect build was failing.

**What the output means:** environment=staging, version=1.0.0, commit=64351fe, image_tag=1.0.0-64351fe.

**What I will tell the professor:** "Staging stayed on the previous version because the defective build never reached the deploy stage."

## Step 15 - The corrective commit: build 3 is green and staging moves [video 06:24]

**Spoken script (as in the video):**

> After the corrective commit, build three ran the same pipeline. All stages are green. Its deployment record shows the staging environment now runs version one point zero point zero, commit three zero c six a zero five, the corrected code. So the pipeline blocked the defective version, and released the fixed one.

**What the output means:** Build #3 page with a success icon, then deployment.txt with commit=30c6a05 and image_tag=1.0.0-30c6a05.

**What I will tell the professor:** "The corrective commit passed all stages and staging moved to the fixed version."

## Step 16 - Build 9: the fix for stale reports works [video 06:47]

**Spoken script (as in the video):**

> After I fixed the stale report problem, I repeated the experiment as build number nine. It fails on the same test. But look at its test result: only the tests that really ran. There is no tests dot e2e package any more. The report does not claim Selenium tests that did not happen. Eighty one passed, one failed, total eighty two.

**What the output means:** Test Result with 1 failure, 81 passed and no tests.e2e package.

**What I will tell the professor:** "After the fix, a failed build no longer shows test results from an older build."

## Step 17 - Build 9: no stale artifacts either [video 07:13]

**Spoken script (as in the video):**

> And the artifacts of build nine: only the one test report that this build produced. No source archive, no deployment record, no health file from earlier builds. The same bug can no longer happen.

**What the output means:** The artifact list contains only the unit-integration-tests.xml report.

**What I will tell the professor:** "A failed build now publishes only its own files."

## Step 18 - Every build now starts clean [video 07:28]

**Spoken script (as in the video):**

> This is the fix, in every build log, here build eleven: the very first command after checkout is rm minus rf reports dist. Old outputs are deleted before anything runs, so a build can never reuse an old report as if it were new. That closes the experiment: the defect was caught by the tests, deployment was blocked, the fix was released, and a bug in the pipeline itself was found and fixed.

**What the output means:** Highlighted: '+ rm -rf reports dist' near the top of the console.

**What I will tell the professor:** "Every build deletes old reports first, so a stale report can never be mistaken for a new one."
