# Task 4 - command sheet

**Task 4 - Git and GitHub Repository Initialization**

## Before you start

- Git installed (`git --version`). Nothing else needs to be running.
- The GitHub step reads the public repository over the internet (read-only, no login). If you are offline, open https://github.com/KemNxts/hotel-room-booking-cicd in a browser instead.
- Open PowerShell in the project folder. These commands only read the repository; none of them changes it.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | The repository and its key files | `Get-ChildItem -Force -Name \| Select-String '^(README\|CONTRIBUTING\|VERSION\|\.git)'` | .git (the history), .github (templates), .gitattributes, .gitignore, CONTRIBUTING.md, README.md, VERSION. |
| 2 | README: the front page | `Get-Content README.md \| Select-Object -First 14` | Project title, a one paragraph description, the current release in the VERSION file, and pointers to the project report and the 15-task checklist. |
| 3 | .gitignore: what Git must not store | `(Get-Content .gitignore \| Select-String -NotMatch '^\s*(#\|$)') -join '  '; git check-ignore -v deploy/jenkins/.env instance/hotel.db .venv` | The list of ignore patterns, then three lines of the form '.gitignore:27:.env   deploy/jenkins/.env', showing the rule that ignores each file. |
| 4 | .gitattributes: line endings | `Get-Content .gitattributes` | '* text=auto eol=lf' stores LF line endings; .bat and .ps1 keep CRLF; images are marked binary. |
| 5 | CONTRIBUTING: the team rules | `Get-Content CONTRIBUTING.md \| Select-Object -First 24` | A table of branches (main, develop, feature/*) with their purpose and who merges into them, followed by the naming rules. |
| 6 | Issue templates | `Get-ChildItem .github -Recurse -File \| Resolve-Path -Relative; Get-Content .github/ISSUE_TEMPLATE/feature_request.md` | Three template files, then the content of the feature request template. |
| 7 | Pull request template and review checklist | `Get-Content .github/pull_request_template.md \| Select-Object -First 22` | Sections: What does this PR do, How was it tested, and the author checklist with seven boxes. |
| 8 | Branches that exist today | `git status --short --branch; git branch` | The current branch with a star, then 20 local branches: main, develop, feature/*, fix/*, experiment/*, docs/*. Untracked files in the demonstrations folder are this recording work. |
| 9 | History as a graph | `git log --oneline --graph --decorate -20` | A graph of commits; merge commits named 'Merge branch feature/... into develop', each with the feature's own commits beside it. |
| 10 | Tags and the remote | `git tag -n1; git remote -v` | Two tags with their messages, and origin fetch/push URLs of the public GitHub repository. |
| 11 | Local repository versus the GitHub repository | `$u = 'https://api.github.com/repos/KemNxts/hotel-room-booking-cicd'; $r = Invoke-RestMethod $u; "$($r.full_name)  public=$(-not $r.private)  default=$($r.default_branch)"; "branches on GitHub: $((Invoke-RestMethod "$u/branches?per_page=100").Count)"; 'tags on GitHub: ' + ((Invoke-RestMethod "$u/tags").name -join ', '); git log --oneline -1 develop; git log --oneline -1 origin/develop` | KemNxts/hotel-room-booking-cicd public=True default=main; 19 branches; tags v1.1.0, v1.0.0; the same commit id for develop and origin/develop. |
| 12 | Anatomy of one commit | `git show --stat --format='commit %h%nAuthor: %an%nDate:   %ad%n%n    %s' --date=short feature/nights-column` | Commit 2d67e39 'feat: show number of nights in the My bookings list' changing a template and a test file (10 insertions, 1 deletion). |

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- Every branch, local and remote:

  ```powershell
  git branch -a
  ```

- The whole history as a graph, all branches:

  ```powershell
  git log --graph --oneline --all
  ```

- Why a file is ignored:

  ```powershell
  git check-ignore -v deploy/jenkins/.env
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| `git` is not recognised | Install Git for Windows or open the 'Git Bash' / VS Code terminal where it is on the PATH. |
| 'fatal: not a git repository' | You are in the wrong folder. `cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING`. |
| Different branch name / commit IDs than in the video | Normal: history moves on. Explain the idea (branches, tags, remote) with what your screen shows. `git switch develop` is safe if there is nothing uncommitted (`git status` first). |
| GitHub request fails (rate limit or offline) | Open the repository page in a browser: it shows 19 branches and the tags v1.0.0 and v1.1.0. |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 04
```
