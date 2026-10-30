# Task 2 - command sheet

**Task 2 - Agile Planning and DevOps Workflow**

## Before you start

- Nothing needs to be running. Only the live test step needs the project's `.venv`.
- The GitHub step reads the public repository's issue count over the internet (read-only); if you are offline, skip it and say the repository has no issues yet.
- Open PowerShell in the project folder.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | What the Agile plan document contains | `Select-String -Path docs/02-agile-plan.md -Pattern '^## ' \| Select-Object LineNumber, Line` | Six headings with their line numbers: stories, backlog, Kanban board, sprint plan, Definition of Done, lifecycle. |
| 2 | User stories | `Select-String -Path docs/02-agile-plan.md -Pattern '^\\| US' \| ForEach-Object { ($_.Line -split '\\|')[1,2] -join ' ->' }` | Nine stories, US1 to US9, each as 'As a ... I want ...'. |
| 3 | Acceptance criteria | `(Select-String -Path docs/02-agile-plan.md -Pattern '^\\| US5').Line` | One table row: story US5 with its criteria and the test names TestCancelBooking and test_journey_4. |
| 4 | Proving story 5 with its tests, live | `pytest tests/unit/test_booking_service.py -k cancel -v --no-header` | 7 passed, 31 deselected. Each line is one test name with PASSED; 'deselected' means other tests were skipped on purpose. |
| 5 | Product backlog | `Select-String -Path docs/02-agile-plan.md -Pattern '^\\| HB-' \| ForEach-Object { ($_.Line -split '\\|')[1,2,3,5] -join ' \|' }` | Fifteen rows HB-01 to HB-15, each with its course task number and status Done. |
| 6 | GitHub issues: the honest status | `$r = Invoke-RestMethod https://api.github.com/repos/KemNxts/hotel-room-booking-cicd; "open issues on GitHub: $($r.open_issues_count)"; Get-ChildItem .github -Recurse -File \| Resolve-Path -Relative` | 'open issues on GitHub: 0', then the three template files: bug report, feature request and pull request template. |
| 7 | Kanban board | `Get-Content docs/02-agile-plan.md \| Select-Object -Skip 41 -First 12` | A five-column table; HB-01 to HB-15 are in Done; payments, admin UI and auto-expiry stay in Backlog. |
| 8 | Sprint plan | `Get-Content docs/02-agile-plan.md \| Select-Object -Skip 53 -First 13` | Three sprints with days, goals and the backlog items in each; a note about the footer branches that conflicted and how that was fixed. |
| 9 | Definition of Done | `Get-Content docs/02-agile-plan.md \| Select-Object -Skip 66 -First 12` | Seven numbered conditions. Items 3 and 4 are enforced automatically by Jenkins. |
| 10 | DevOps lifecycle diagram | `Get-Content docs/02-agile-plan.md \| Select-Object -Skip 79` | Mermaid diagram source: boxes Plan, Code, Build, Test, Release, Deploy, Operate, Monitor, Rollback, with an arrow that stops the flow when a test fails. |
| 11 | The lifecycle in the real pipeline | `Select-String -Path Jenkinsfile -Pattern "stage\('" \| ForEach-Object { $_.Line.Trim() }` | Ten stage names. Test stages come before Package, Build, Publish and Deploy, which is the quality gate. |

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- Open the plan with the lifecycle diagram drawn (VS Code preview or GitHub):

  ```powershell
  code docs/02-agile-plan.md
  ```

- Show the issue template that is ready for creating backlog issues:

  ```powershell
  Get-Content .github/ISSUE_TEMPLATE/feature_request.md
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| `pytest` is not recognised | Use `.venv\Scripts\pytest ...`, or create the environment: `python -m venv .venv` then `.venv\Scripts\pip install -r requirements-dev.txt`. |
| GitHub step prints an error | No internet or GitHub rate limit. Open https://github.com/KemNxts/hotel-room-booking-cicd/issues in a browser instead; it shows 0 open and 0 closed issues. |
| Line ranges are shifted | The document was edited. Open `docs/02-agile-plan.md` in VS Code preview (Ctrl+Shift+V) and scroll to the section. |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 02
```
