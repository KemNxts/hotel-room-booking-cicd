# Task 5 - command sheet

**Task 5 - Feature Development with Branching**

## Before you start

- Git installed. Nothing else needs to be running.
- The real-history steps only read the project repository. The practice steps create three throw-away repositories under your TEMP folder (git-practice, git-practice-remote.git, git-practice-mate) and delete them at the end; they never touch the project.
- The last pull-request step reads the public GitHub repository (read-only). If you are offline, skip that line and say that no pull requests exist on GitHub yet.
- Open PowerShell in the project folder.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | Every feature was merged into develop | `git log --merges --first-parent --oneline develop \| Select-Object -First 15` | Fifteen lines of the form 'Merge branch feature/... into develop', newest first. |
| 2 | One real feature: security hardening | `git log --oneline bdfc2fb^1..bdfc2fb^2` | Two commits: 'feat: add CSRF protection...' and 'test: add route-level integration tests...'. |
| 3 | The files that feature changed | `git diff --stat bdfc2fb^1 bdfc2fb^2 \| Select-Object -Last 18` | 17 files changed: app/controllers/csrf.py new, schema.sql triggers, templates, and tests; 459 insertions, 18 deletions. |
| 4 | The merge commit and its two parents | `git show --no-patch --format='%h %s%nparents: %p' bdfc2fb` | 'Merge branch feature/security-hardening into develop' with two parent commit IDs. |
| 5 | Practice repository: git add and git commit | `$s = "$env:TEMP/git-practice"; $remote = "$env:TEMP/git-practice-remote.git"; $mate = "$env:TEMP/git-practice-mate"; Remove-Item $s,$remote,$mate -Recurse -Force -ErrorAction SilentlyContinue; git init -q --bare -b develop $remote; git init -q -b develop $s; git -C $s config user.name Practice; git -C $s config user.email practice@example.com; Set-Content "$s/README.md" 'Practice repo'; git -C $s add README.md; git -C $s commit -q -m 'chore: first commit'; git -C $s log --oneline` | One commit 'chore: first commit' on the practice repository. |
| 6 | Practice: a feature branch, then stage and commit | `git -C $s switch -c feature/room-search; Add-Content "$s/README.md" 'Room search feature'; git -C $s status --short; git -C $s add README.md; git -C $s status --short; git -C $s commit -q -m 'feat: describe room search'; git -C $s log --oneline` | ' M README.md' (modified, not staged), then 'M  README.md' (staged), then two commits on the feature branch. |
| 7 | Practice: git push | `git -C $s remote add origin $remote; git -C $s push -u origin feature/room-search; git -C $s branch -vv` | '[new branch] feature/room-search -> feature/room-search', and the branch list showing it tracks origin/feature/room-search. |
| 8 | Practice: merge the feature into develop | `git -C $s switch develop; git -C $s merge --no-ff --no-edit feature/room-search; git -C $s log --graph --oneline` | 'Merge made by the ort strategy' and a graph with a merge commit joining the feature commit into develop. |
| 9 | Practice: git pull brings a teammate's work | `git -C $s push -q -u origin develop; git clone -q $remote $mate; git -C $mate config user.name Teammate; git -C $mate config user.email mate@example.com; Add-Content "$mate/README.md" 'Teammate edit'; git -C $mate commit -q -am 'docs: teammate edit'; git -C $mate push -q; git -C $s pull` | 'Updating ... Fast-forward' and 'README.md / 1 +', meaning my develop received the teammate's commit. |
| 10 | Pull requests and code review: the honest status | `Get-Content docs/pull-requests/feature-security-hardening.md \| Select-Object -First 15; 'Pull requests on GitHub: ' + (Invoke-RestMethod 'https://api.github.com/repos/KemNxts/hotel-room-booking-cicd/pulls?state=all').Count` | The prepared PR description (summary, tests, checklist) and then 'Pull requests on GitHub: 0'. |
| 11 | Clean up and confirm the project is untouched | `Remove-Item $s,$remote,$mate -Recurse -Force; 'practice folder exists: ' + (Test-Path $s); git status --short --branch` | 'practice folder exists: False' and the project's own branch with only the untracked demonstrations folder listed. |

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- See the files of any merged feature (replace the branch):

  ```powershell
  git diff --stat develop...feature/nights-column
  ```

- Real old-to-new commit ID map (history was rewritten once):

  ```powershell
  Get-Content docs/evidence/git/commit-id-map.md
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| `git init -b` is not recognised | Your Git is older than 2.28. Update Git for Windows, or use `git init` then `git branch -M develop`. |
| Practice step fails because the folder already exists | `Remove-Item $env:TEMP/git-practice, $env:TEMP/git-practice-remote.git, $env:TEMP/git-practice-mate -Recurse -Force -ErrorAction SilentlyContinue`, then start again from the first practice step. |
| 'Author identity unknown' | The practice steps set a local name and email inside the practice repository. If you skipped that line: `git -C $s config user.name Practice` and `git -C $s config user.email practice@example.com`. |
| The merge IDs differ from the video | Use the branch names, not the IDs: `git log --merges --first-parent --oneline develop` shows the real merge commits on your machine. |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 05
```
