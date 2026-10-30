# Task 6 - narration script

**Task 6 - MVP Completion and Git Collaboration**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

# Part: Task 6 (part 1) - The six booking features in the real web application

## Step 1 - The portal and the six features [video 00:01]

**What I am doing:** Open the home page /rooms of the running application.

**Spoken script (as in the video):**

> This is part one of Task 6. It is the real Grand Stay Hotel portal running on this laptop, with a temporary database. I will use all six features as a guest: register and log in, check room availability by date, request a booking, confirm it, cancel it, and track the status of my bookings. Watch the red outline: it marks what is clicked.

**What the output means:** The room list page with the Log in and Register links in the navigation.

**What I will tell the professor:** "This is the real application, and I will now use all six features as a guest."

## Step 2 - Feature 1: registration [video 00:27]

**What I am doing:** Open /register, type full name, e-mail and password, click 'Create account'.

**Spoken script (as in the video):**

> Feature one, registration. A new guest types a full name, an email and a password of at least eight characters, then clicks Create account. The account is created, the guest is logged in automatically, the name appears in the navigation bar, and a green message confirms it. The password is stored only as a salted hash, never as plain text.

**What the output means:** A green flash message 'account has been created', the guest's name in the navigation bar and the room list.

**What I will tell the professor:** "Registration creates an account and logs the guest in; passwords are stored as hashes."

## Step 3 - Feature 1: login and a wrong password [video 00:53]

**What I am doing:** Click 'Log out'. On the login page enter the e-mail with a wrong password, click 'Log in'; then enter the right password and click 'Log in'.

**Spoken script (as in the video):**

> Now login. I log out, then try a wrong password. The message says invalid email or password, and it does not say which of the two was wrong, so an attacker cannot find out which emails exist. Then I type the right password, and the portal says welcome back. Login works, and bad credentials are refused.

**What the output means:** First an error flash 'Invalid email or password', then 'Welcome back' and the guest's name in the navigation.

**What I will tell the professor:** "Login refuses a wrong password with a message that does not reveal whether the email exists."

## Step 4 - Feature 2: room availability by date [video 01:17]

**What I am doing:** Open /rooms, choose check-in and check-out dates, click 'Check availability'.

**Spoken script (as in the video):**

> Feature two, room availability. I choose a check in date and a check out date two nights later, and click Check availability. The table shows each of the six rooms as Available or Booked for exactly those dates, with the type and price. Dates in the past, or a check out before the check in, would be refused with a message.

**What the output means:** A table of the six rooms with an Available badge for each, because nothing is booked yet.

**What I will tell the professor:** "The availability search shows each room as available or booked for the chosen dates."

## Step 5 - Feature 3: booking request [video 01:40]

**What I am doing:** Click the 'Book room ...' button of the first available room.

**Spoken script (as in the video):**

> Feature three, booking request. I click Book on the first free room. The system creates a booking with the status PENDING. It shows the dates and the total price, which is the number of nights times the price per night. Pending means requested, but not yet confirmed.

**What the output means:** The booking page: status PENDING, check-in and check-out dates, total price, and Confirm and Cancel buttons.

**What I will tell the professor:** "A booking request creates a PENDING booking with the total price calculated."

## Step 6 - Feature 4: booking confirmation [video 02:00]

**What I am doing:** Click 'Confirm booking'.

**Spoken script (as in the video):**

> Feature four, confirmation. I click Confirm booking. The status changes from PENDING to CONFIRMED and a message says booking confirmed. The confirm button disappears, because a booking cannot be confirmed twice. The allowed changes are fixed: pending to confirmed, and pending or confirmed to cancelled.

**What the output means:** Status CONFIRMED, the flash 'Booking confirmed' and no Confirm button any more.

**What I will tell the professor:** "Confirmation moves the booking from PENDING to CONFIRMED, and only once."

## Step 7 - No double booking: a second guest [video 02:23]

**What I am doing:** Log out, register a second guest, search the same dates, observe the booked room; log out and log the first guest in again.

**Spoken script (as in the video):**

> Now the most important rule, no double booking. I log out, register a second guest, Ben, and search the same dates. The room that Asha booked is now shown as Booked, and there is no Book button for it. The system protects this twice: in the code, and with a database trigger. Then I log Asha back in.

**What the output means:** The room booked earlier shows a Booked badge and has no Book button for the second guest.

**What I will tell the professor:** "A confirmed room is unavailable to other guests, which prevents double bookings."

## Step 8 - Feature 6: status tracking in My bookings [video 02:46]

**What I am doing:** Search other dates, book a room, click 'My bookings'.

**Spoken script (as in the video):**

> Feature six, status tracking. Asha makes a second booking for other dates, which is PENDING, then opens My bookings. This page lists only her own bookings, with the room, the dates, the nights and the current status: one CONFIRMED and one PENDING. Guests no longer need to phone the hotel to ask whether their booking is confirmed.

**What the output means:** A table with two rows: the first booking CONFIRMED and the new one PENDING.

**What I will tell the professor:** "My bookings shows each of my bookings with its current status, so no phone call is needed."

## Step 9 - Feature 5: cancellation, and the room is free again [video 03:10]

**What I am doing:** Open the booking, click 'Cancel booking', then 'Yes, cancel booking'; open My bookings; search the same dates again.

**Spoken script (as in the video):**

> Feature five, cancellation. I open the confirmed booking and click Cancel booking. A dialog asks me to confirm, so nothing is cancelled by accident. After I accept, the status is CANCELLED. My bookings shows it, and when I search the same dates again, the room is Available again, because cancelled bookings do not block a room.

**What the output means:** Status CANCELLED, the My bookings row marked CANCELLED, and the room's badge back to Available.

**What I will tell the professor:** "Cancelling needs a confirmation, updates the status, and frees the room."

## Step 10 - Where the DevOps side connects: /health [video 03:36]

**What I am doing:** Open /health.

**Spoken script (as in the video):**

> Finally, the health page. It reports the status, the environment and the version of the running application. Later tasks use exactly this address to check that a deployment, or a rollback, put the right version in place. All six features work, and the application also identifies itself.

**What the output means:** A small JSON document: status ok, env, version and commit.

**What I will tell the professor:** "All six features work, and the app reports its own version for the pipeline to check."

# Part: Task 6 (part 2) - Git collaboration: merge conflict, resolution and release tags

## Step 11 - Two features built in parallel [video 04:00]

**What I am doing:** running

```powershell
git log --graph --oneline -7 9e766ac; 'common starting point: ' + (git merge-base feature/contact-footer feature/release-footer).Substring(0,7)
```

**Spoken script (as in the video):**

> This is the Git collaboration part of Task 6. Two developers, or here two feature branches, were started from the same commit on develop. One added the hotel contact footer, the other added a footer showing the running release. Look at this graph. The two side lines branch from the same point and merge back one after the other. The common starting point is printed below.

**What the output means:** A graph with two feature commits (contact details, running release) side by side, each merged into develop by its own merge commit, and the shared base commit id.

**What I will tell the professor:** "Two people changed the same footer at the same time from the same starting point, which is exactly how conflicts arise."

## Step 12 - The saved record of the real conflict [video 04:30]

**What I am doing:** running

```powershell
Get-Content docs/evidence/git/merge-conflict.txt | Select-Object -First 17
```

**Spoken script (as in the video):**

> When this happened in the project, I saved the unedited terminal output. Merging the second feature printed conflict in three files: style dot css, base dot html and the integration tests. Git merged what it could, and stopped, saying the automatic merge failed. The status lines starting with U U mean unmerged on both sides.

**What the output means:** 'CONFLICT (content): Merge conflict in ...' for three files, 'Automatic merge failed', and git status showing 'UU' for the three files.

**What I will tell the professor:** "This is the original output from when the conflict really happened."

## Step 13 - Reproducing the conflict live, safely [video 04:58]

**What I am doing:** running

```powershell
$c = "$env:TEMP/conflict-demo"; Remove-Item $c -Recurse -Force -ErrorAction SilentlyContinue; git clone -q . $c; git -C $c config user.name Practice; git -C $c config user.email practice@example.com; git -C $c switch -q --detach 4463add; git -C $c merge --no-commit 63498a8; 'unmerged files:'; git -C $c diff --name-only --diff-filter=U
```

**Spoken script (as in the video):**

> To show that it is real, I reproduce it now in a disposable clone in the temporary folder, so the project is not touched. I clone the repository, go to the commit where the contact footer was already merged, and try to merge the release footer branch. Git reports the same three conflicts, exactly as in the saved evidence.

**What the output means:** The same three CONFLICT lines, 'Automatic merge failed', then the three unmerged files.

**What I will tell the professor:** "I can reproduce the conflict on demand; it is a real Git conflict, not a screenshot."

## Step 14 - Reading the conflict markers [video 05:24]

**What I am doing:** running

```powershell
Get-Content -Encoding UTF8 "$c/app/templates/base.html" | Select-Object -Last 11
```

**Spoken script (as in the video):**

> This is how Git shows a conflict inside the file. The line with seven less than signs and HEAD starts our side, the contact footer. The line of equals signs separates the two versions. The line with seven greater than signs ends the other side, the release footer. Git cannot know which to keep, so a person must decide. Here both lines are wanted.

**What the output means:** The footer element containing <<<<<<< HEAD, the hotel-contact span, =======, the app-version span, >>>>>>> and the commit id.

**What I will tell the professor:** "Git marks both versions in the file and waits for a person to decide."

## Step 15 - The resolution: keep both [video 05:52]

**What I am doing:** running

```powershell
git show 9e766ac:app/templates/base.html | Select-Object -Last 10; git show 9e766ac:app/static/style.css | Select-String 'site-footer' | ForEach-Object { $_.Line.Trim() }
```

**Spoken script (as in the video):**

> This is the real resolved file from the actual merge commit. Both features were wanted, so the resolution keeps both lines: the contact line first, the release line below. The style sheet got one combined footer rule, and each line sits on its own row. Nothing from either developer was lost.

**What the output means:** The footer with both spans and no markers, then the combined .site-footer CSS rules.

**What I will tell the professor:** "Both intended changes were preserved: the contact line and the release line."

## Step 16 - Tests and the merge commit message [video 06:17]

**What I am doing:** running

```powershell
git show 9e766ac:tests/integration/test_routes.py | Select-String 'def test_.*(footer|contact|release)' | ForEach-Object { $_.Line.Trim() }; git show --no-patch --format=%B 9e766ac
```

**Spoken script (as in the video):**

> The third conflicted file was the test file. Both new tests were kept, one for the contact details and one for the release footer. And the merge commit message documents the whole decision: what was in conflict in each file, what was kept, and that the linter was clean and all eighty nine tests passed before committing. That is good practice.

**What the output means:** Two test functions (contact details, running release), then the merge message listing the resolution of each file and the verification result.

**What I will tell the professor:** "I kept both tests, and I verified flake8 and the full test suite before committing the merge."

## Step 17 - Abort and clean up [video 06:43]

**What I am doing:** running

```powershell
git -C $c merge --abort; Remove-Item $c -Recurse -Force; 'disposable clone exists: ' + (Test-Path $c); git status --short --branch
```

**Spoken script (as in the video):**

> Back in the practice clone I abort the merge, which returns it to the state before the merge, then delete the clone. Then I show that my real project repository is unchanged.

**What the output means:** 'disposable clone exists: False' and the project's own branch with only the untracked demonstrations folder.

**What I will tell the professor:** "The demonstration happened in a throw-away clone and left the project unchanged."

## Step 18 - Release tags v1.0.0 and v1.1.0 [video 06:58]

**What I am doing:** running

```powershell
git tag -n1; foreach ($t in 'v1.0.0','v1.1.0') { git log -1 --format="$t -> %h  %s" $t; "VERSION file inside ${t}: " + (git show "${t}:VERSION") }
```

**Spoken script (as in the video):**

> Now the release tags. A tag is a permanent label on one commit that marks a release. We have v1.0.0, the first complete version, and v1.1.0, which adds the nights column. For each tag I print the commit it points to, and the VERSION file as it was inside that tag. So the tag really contains the released version.

**What the output means:** Both tags with their messages, the commit each points to ('release: v1.0.0', 'release: v1.1.0') and VERSION 1.0.0 and 1.1.0.

**What I will tell the professor:** "Each release is a tag that points to one exact commit and contains that version number."

## Step 19 - Branch versus tag [video 07:26]

**What I am doing:** running

```powershell
git describe --tags main; 'commits on main after v1.1.0: ' + (git rev-list --count v1.1.0..main); 'v1.1.0 still points at: ' + (git log -1 --format=%h v1.1.0)
```

**Spoken script (as in the video):**

> What is the difference between a branch and a tag? A branch is a moving line of development, it advances with every new commit. A tag stays fixed on one commit. Proof: main has moved on eleven commits since the v1.1.0 tag, mostly documentation, but the tag still points to the same release commit. Git describe prints exactly that: the tag name, eleven commits ahead.

**What the output means:** 'v1.1.0-11-g...', 'commits on main after v1.1.0: 11' and the unchanged release commit id.

**What I will tell the professor:** "A branch is a line of development that moves; a tag marks one specific point in history forever."
