# Task 6 - command sheet

**Task 6 - MVP Completion and Git Collaboration**

## Before you start

- Chrome installed (Selenium downloads a matching chromedriver automatically the first time; internet needed once).
- The `.venv` must contain Flask and Selenium (`.venv\Scripts\pip install -r requirements-dev.txt`).
- The recorder starts the real Flask app itself on a free port with a throw-away database in your TEMP folder. To do the same by hand: `$env:DATABASE_PATH="$env:TEMP/demo.db"; .venv\Scripts\python wsgi.py` and open http://127.0.0.1:5000.
- Do not use the mouse or keyboard while this part is being recorded: the Chrome window must stay on top.
- Git installed. Nothing else needs to be running.
- The conflict is reproduced inside a disposable clone under your TEMP folder (`conflict-demo`), which is deleted at the end. The project repository is never changed.
- Open PowerShell in the project folder.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

### Task 6 (part 1) - The six booking features in the real web application

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | The portal and the six features | `Open the home page /rooms of the running application.` | The room list page with the Log in and Register links in the navigation. |
| 2 | Feature 1: registration | `Open /register, type full name, e-mail and password, click 'Create account'.` | A green flash message 'account has been created', the guest's name in the navigation bar and the room list. |
| 3 | Feature 1: login and a wrong password | `Click 'Log out'. On the login page enter the e-mail with a wrong password, click 'Log in'; then enter the right password and click 'Log in'.` | First an error flash 'Invalid email or password', then 'Welcome back' and the guest's name in the navigation. |
| 4 | Feature 2: room availability by date | `Open /rooms, choose check-in and check-out dates, click 'Check availability'.` | A table of the six rooms with an Available badge for each, because nothing is booked yet. |
| 5 | Feature 3: booking request | `Click the 'Book room ...' button of the first available room.` | The booking page: status PENDING, check-in and check-out dates, total price, and Confirm and Cancel buttons. |
| 6 | Feature 4: booking confirmation | `Click 'Confirm booking'.` | Status CONFIRMED, the flash 'Booking confirmed' and no Confirm button any more. |
| 7 | No double booking: a second guest | `Log out, register a second guest, search the same dates, observe the booked room; log out and log the first guest in again.` | The room booked earlier shows a Booked badge and has no Book button for the second guest. |
| 8 | Feature 6: status tracking in My bookings | `Search other dates, book a room, click 'My bookings'.` | A table with two rows: the first booking CONFIRMED and the new one PENDING. |
| 9 | Feature 5: cancellation, and the room is free again | `Open the booking, click 'Cancel booking', then 'Yes, cancel booking'; open My bookings; search the same dates again.` | Status CANCELLED, the My bookings row marked CANCELLED, and the room's badge back to Available. |
| 10 | Where the DevOps side connects: /health | `Open /health.` | A small JSON document: status ok, env, version and commit. |

### Task 6 (part 2) - Git collaboration: merge conflict, resolution and release tags

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 11 | Two features built in parallel | `git log --graph --oneline -7 9e766ac; 'common starting point: ' + (git merge-base feature/contact-footer feature/release-footer).Substring(0,7)` | A graph with two feature commits (contact details, running release) side by side, each merged into develop by its own merge commit, and the shared base commit id. |
| 12 | The saved record of the real conflict | `Get-Content docs/evidence/git/merge-conflict.txt \| Select-Object -First 17` | 'CONFLICT (content): Merge conflict in ...' for three files, 'Automatic merge failed', and git status showing 'UU' for the three files. |
| 13 | Reproducing the conflict live, safely | `$c = "$env:TEMP/conflict-demo"; Remove-Item $c -Recurse -Force -ErrorAction SilentlyContinue; git clone -q . $c; git -C $c config user.name Practice; git -C $c config user.email practice@example.com; git -C $c switch -q --detach 4463add; git -C $c merge --no-commit 63498a8; 'unmerged files:'; git -C $c diff --name-only --diff-filter=U` | The same three CONFLICT lines, 'Automatic merge failed', then the three unmerged files. |
| 14 | Reading the conflict markers | `Get-Content -Encoding UTF8 "$c/app/templates/base.html" \| Select-Object -Last 11` | The footer element containing <<<<<<< HEAD, the hotel-contact span, =======, the app-version span, >>>>>>> and the commit id. |
| 15 | The resolution: keep both | `git show 9e766ac:app/templates/base.html \| Select-Object -Last 10; git show 9e766ac:app/static/style.css \| Select-String 'site-footer' \| ForEach-Object { $_.Line.Trim() }` | The footer with both spans and no markers, then the combined .site-footer CSS rules. |
| 16 | Tests and the merge commit message | `git show 9e766ac:tests/integration/test_routes.py \| Select-String 'def test_.*(footer\|contact\|release)' \| ForEach-Object { $_.Line.Trim() }; git show --no-patch --format=%B 9e766ac` | Two test functions (contact details, running release), then the merge message listing the resolution of each file and the verification result. |
| 17 | Abort and clean up | `git -C $c merge --abort; Remove-Item $c -Recurse -Force; 'disposable clone exists: ' + (Test-Path $c); git status --short --branch` | 'disposable clone exists: False' and the project's own branch with only the untracked demonstrations folder. |
| 18 | Release tags v1.0.0 and v1.1.0 | `git tag -n1; foreach ($t in 'v1.0.0','v1.1.0') { git log -1 --format="$t -> %h  %s" $t; "VERSION file inside ${t}: " + (git show "${t}:VERSION") }` | Both tags with their messages, the commit each points to ('release: v1.0.0', 'release: v1.1.0') and VERSION 1.0.0 and 1.1.0. |
| 19 | Branch versus tag | `git describe --tags main; 'commits on main after v1.1.0: ' + (git rev-list --count v1.1.0..main); 'v1.1.0 still points at: ' + (git log -1 --format=%h v1.1.0)` | 'v1.1.0-11-g...', 'commits on main after v1.1.0: 11' and the unchanged release commit id. |

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- Run the same journeys as automated tests with a visible browser:

  ```powershell
  $env:HEADLESS='0'; pytest tests/e2e -v
  ```

- Run the app yourself:

  ```powershell
  .venv\Scripts\python wsgi.py   # http://127.0.0.1:5000
  ```

- Read the project's own saved record of the conflict:

  ```powershell
  Get-Content docs/evidence/git/merge-conflict.txt
  ```

- See what the resolution commit changed:

  ```powershell
  git show 9e766ac --stat
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| Chrome does not open / 'session not created' | Chrome and chromedriver versions differ. Update Chrome, or run once with internet so Selenium Manager can fetch the matching driver. |
| The page shows 'This site can't be reached' | The app is not running. Start it (`.venv\Scripts\python wsgi.py`) and open http://127.0.0.1:5000. |
| A room shows 'Booked' for the date you want | Pick other dates, or use a fresh database (`$env:DATABASE_PATH` pointing to a new file). Bookings are kept in the SQLite file. |
| 'Invalid email or password' when you expected success | Passwords are at least 8 characters and the email is case-insensitive. Register a new guest if unsure. |
| The clone folder already exists | `Remove-Item $env:TEMP/conflict-demo -Recurse -Force`, then run the clone step again. |
| 'Author identity unknown' while merging | Set a name and email inside the clone only: `git -C $c config user.name Practice; git -C $c config user.email practice@example.com`. |
| No conflict appears | Check the commit IDs with `git log --graph --oneline -7 9e766ac`. If history changed, use the two merge commits named 'feature/contact-footer' and 'feature/release-footer' that `git log --merges --first-parent --oneline develop` shows. |
| Strange characters instead of the dot in the footer | Use `Get-Content -Encoding UTF8 <file>` (Windows PowerShell 5.1 reads files without a BOM as ANSI). |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 06 -Part app
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 06 -Part git
```
