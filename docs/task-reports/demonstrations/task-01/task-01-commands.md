# Task 1 - command sheet

**Task 1 - Problem Definition and Scope**

## Before you start

- Nothing needs to be running: Task 1 is a document. Only the final test step needs the project's `.venv` (Python virtual environment).
- Open PowerShell (or the VS Code terminal) in the project folder.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | Where the Task 1 document lives | `Get-ChildItem docs -Filter 0*.md \| Select-Object Name, Length` | The docs folder holds numbered documents, one per area; 01 is Task 1. Git history proves it is version-controlled. |
| 2 | Problem statement | `Get-Content docs/01-problem-definition.md \| Select-Object -Skip 2 -First 12` | The first paragraph is the business problem (manual bookings, double bookings); the second is the DevOps problem (unsafe manual releases). |
| 3 | Target users and stakeholders | `Get-Content docs/01-problem-definition.md \| Select-Object -Skip 15 -First 18` | Users use the system; stakeholders are affected by it. Each group wants something different. |
| 4 | Pain points and objectives | `Get-Content docs/01-problem-definition.md \| Select-Object -Skip 34 -First 21` | Six pain points map to seven objectives O1 to O7. O2 (no overlap) and O4 (failing test blocks deploy) are the key ones. |
| 5 | Constraints | `Get-Content docs/01-problem-definition.md \| Select-Object -Skip 55 -First 19` | Constraints explain design choices: SQLite means one writer, no public server means Jenkins polls Git. |
| 6 | Measurable success criteria | `Get-Content docs/01-problem-definition.md \| Select-Object -Skip 74 -First 13` | Each row has a target and the evidence that it was achieved, e.g. 90 tests, changed=0 on repeat Ansible run. |
| 7 | Proving one criterion live: the automated tests | `pytest -q -m "not e2e"` | pytest prints one dot per passing test and a summary line such as '85 passed, 5 deselected'. Deselected are the 5 browser tests that this command skips. |
| 8 | Approved MVP scope | `Get-Content docs/01-problem-definition.md \| Select-Object -Skip 87 -First 17` | The MVP is the 6 workflows; payments, admin UI and e-mail are listed as out of scope on purpose. |

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- Read the whole document with a preview in VS Code:

  ```powershell
  code docs/01-problem-definition.md
  ```

- Show which commits changed the document:

  ```powershell
  git log --oneline -- docs/01-problem-definition.md
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| `pytest` is not recognised | Use `.venv\Scripts\pytest -q -m "not e2e"`. If `.venv` is missing: `python -m venv .venv` then `.venv\Scripts\pip install -r requirements-dev.txt`. |
| Some tests fail | Read the first failure message. Run `git status` - you may be on an unfinished branch. `git switch develop` and run again. |
| Line ranges in the document look shifted | The document was edited. Open `docs/01-problem-definition.md` in VS Code (Ctrl+Shift+V for preview) and scroll instead of using -Skip / -First. |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 01
```
