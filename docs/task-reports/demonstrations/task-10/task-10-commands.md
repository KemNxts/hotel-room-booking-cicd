# Task 10 - command sheet

**Task 10 - Continuous Testing in Jenkins**

## Before you start

- Git and the project `.venv` (pytest). Nothing else needs to be running.
- The live reproduction happens in a disposable clone under your TEMP folder (`defect-demo`), deleted at the end. The defect is never created in your project or on any branch of it.
- Open PowerShell in the project folder.
- Jenkins running at http://localhost:8090 with its original build history (the jenkins-home volume). If that volume was deleted, builds #2, #3 and #9 no longer exist; use the saved logs in docs/evidence/jenkins/ instead.
- Log in to Jenkins before the demo so the password is not typed in front of the examiner.
- Everything here is read-only: it opens old builds and does not start a build.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

### Task 10 (part 1) - The defect experiment: code, a live failing test, and the stale-report fix

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | How a failing test stops the pipeline | `Select-String -Path Jenkinsfile -Pattern "stage\('\|pytest\|junit \|rm -rf reports" \| ForEach-Object { '{0,3}: {1}' -f $_.LineNumber, $_.Line.Trim() }` | Stage names with line numbers, the two pytest commands (unit/integration and e2e), 'rm -rf reports dist' in Checkout, and the junit step in post. |
| 2 | The experiment branch: a deliberate defect | `git log --oneline develop..experiment/defect-demo; 'branches that contain the defect commit:'; git branch --contains 5844eec` | Two commits (the experiment commit and the fix) and only experiment/defect-demo and experiment/defect-demo-2 containing the defect. |
| 3 | The defect: one character | `git diff 5844eec^ 5844eec -- app/dao/booking_dao.py` | A one-line diff: '-    check_in < :check_out' and '+    check_in <= :check_out' in _OVERLAP_SQL. |
| 4 | Live: the tests catch the defect | `$d = "$env:TEMP/defect-demo"; Remove-Item $d -Recurse -Force -ErrorAction SilentlyContinue; git clone -q . $d; git -C $d checkout -q 5844eec; Push-Location $d; python -m pytest tests/unit tests/integration -q -p no:cacheprovider 2>&1 \| Select-Object -Last 6; 'pytest exit code: ' + $LASTEXITCODE; Pop-Location` | FAILED ...test_overlap_rules[...] near the end, '1 failed, ... passed' (or similar) and 'pytest exit code: 1'. |
| 5 | Live: the corrective commit makes it green | `git -C $d checkout -q 2fb62d6; Push-Location $d; python -m pytest tests/unit tests/integration -q -p no:cacheprovider 2>&1 \| Select-Object -Last 3; 'pytest exit code: ' + $LASTEXITCODE; Pop-Location; git show 2fb62d6 --format='%h %s' -- app/dao/booking_dao.py \| Select-Object -First 12` | '82 passed' (the unit and integration tests that existed at that commit; Jenkins added the 5 browser tests for 87), exit code 0, then the one-line fix diff restoring '<'. |
| 6 | Clean up the disposable clone | `Remove-Item $d -Recurse -Force; 'clone exists: ' + (Test-Path $d); git status --short --branch` | 'clone exists: False' and the project's own branch with only the untracked demonstrations folder. |
| 7 | The stale test report bug and its fix | `git show 32d5f8e --format='%h %s' -U1 -- Jenkinsfile \| Select-Object -First 16` | The commit 'fix: stop Jenkins publishing stale test reports from earlier builds' adding the comment lines and sh 'rm -rf reports dist' to the Checkout stage. |
| 8 | Commit IDs in the Jenkins evidence | `Select-String -Path docs/evidence/git/commit-id-map.md -Pattern '554cad3\|30c6a05\|8505486' \| ForEach-Object { $_.Line }` | Table rows mapping 554cad3 -> 5844eec, 30c6a05 -> 2fb62d6 and 8505486 -> a3d8626 with their subjects. |

### Task 10 (part 2) - The defect experiment in Jenkins: real builds #1, #2, #3, #9 and #11

| # | Step | Command / action | Expected result |
|---|---|---|---|

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- Which branches contain the defect commit (proves it was never merged):

  ```powershell
  git branch --contains 5844eec
  ```

- The real Jenkins console log of the failed build #2:

  ```powershell
  Get-Content docs/evidence/jenkins/build-02-defect-fails.log | Select-Object -Last 40
  ```

- Open the failed build in your browser:

  ```powershell
  Start-Process http://localhost:8090/job/hotel-booking/2/
  ```

- Read the saved log of the failed build:

  ```powershell
  Get-Content docs/evidence/jenkins/build-02-defect-fails.log | Select-Object -Last 45
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| The clone folder already exists | `Remove-Item $env:TEMP/defect-demo -Recurse -Force`, then run the clone step again. |
| `pytest` runs the wrong project's tests | The command must run inside the clone: `Push-Location $d; python -m pytest ...; Pop-Location`. Check with `Get-Location` that you are in the clone. |
| Commit IDs from the documents are not found | The history was rewritten once; see docs/evidence/git/commit-id-map.md for old to new IDs. Branch names are unchanged: experiment/defect-demo and experiment/defect-demo-2. |
| Build #2 / #3 / #9 not found (404) | The Jenkins history was reset. Use docs/evidence/jenkins/build-02-defect-fails.log, build-03-fix-green.log and build-09-defect-rerun-after-report-fix.log, and the screenshots jenkins-04-build2-defect.png and jenkins-05-build2-failed-test.png in docs/evidence/screenshots/. |
| The pages ask for a login | Log in as admin first (password in deploy/jenkins/.env, never show that file). |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 10 -Part git
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 10 -Part ui
```
