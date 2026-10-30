# Task 5 - narration script

**Task 5 - Feature Development with Branching**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

## Step 1 - Every feature was merged into develop [video 00:01]

**What I am doing:** running

```powershell
git log --merges --first-parent --oneline develop | Select-Object -First 15
```

**Spoken script (as in the video):**

> This is Task 5, feature development with branching. A feature branch is a separate line of development for one feature, so unfinished work never disturbs the stable code. This command lists the merge commits on the develop branch. Each line is one feature or fix branch that was merged: app mvp, tests, docker, jenkins pipeline, ansible, security hardening and more. This is the real project history.

**What the output means:** Fifteen lines of the form 'Merge branch feature/... into develop', newest first.

**What I will tell the professor:** "Every feature was built on its own branch and merged into develop."

## Step 2 - One real feature: security hardening [video 00:33]

**What I am doing:** running

```powershell
git log --oneline bdfc2fb^1..bdfc2fb^2
```

**Spoken script (as in the video):**

> Let me follow one feature, security hardening. On its branch there are two commits. The first adds the CSRF protection, secure cookies and a database guard against overlapping bookings. The second adds the tests for them. The prefixes feat and test follow our commit convention. Small commits, one purpose each.

**What the output means:** Two commits: 'feat: add CSRF protection...' and 'test: add route-level integration tests...'.

**What I will tell the professor:** "The feature is two focused commits, the code and its tests."

## Step 3 - The files that feature changed [video 00:59]

**What I am doing:** running

```powershell
git diff --stat bdfc2fb^1 bdfc2fb^2 | Select-Object -Last 18
```

**Spoken script (as in the video):**

> These are the feature files. The controllers got a CSRF check, the schema got the database triggers, the templates got the token field, and there are new integration tests. Seventeen files, mostly additions, and no unrelated changes. A reviewer can understand the whole feature from this list.

**What the output means:** 17 files changed: app/controllers/csrf.py new, schema.sql triggers, templates, and tests; 459 insertions, 18 deletions.

**What I will tell the professor:** "The branch contains only the files that belong to this feature."

## Step 4 - The merge commit and its two parents [video 01:24]

**What I am doing:** running

```powershell
git show --no-patch --format='%h %s%nparents: %p' bdfc2fb
```

**Spoken script (as in the video):**

> Now the merge itself. This merge commit has two parents: the previous tip of develop, and the last commit of the feature branch. We merged with the no fast forward option, so Git always creates this merge commit, and the history shows the feature as one unit. If this feature had to be undone, we would revert this single commit.

**What the output means:** 'Merge branch feature/security-hardening into develop' with two parent commit IDs.

**What I will tell the professor:** "The merge commit joins the feature branch back into develop and keeps the feature visible in history."

## Step 5 - Practice repository: git add and git commit [video 01:49]

**What I am doing:** running

```powershell
$s = "$env:TEMP/git-practice"; $remote = "$env:TEMP/git-practice-remote.git"; $mate = "$env:TEMP/git-practice-mate"; Remove-Item $s,$remote,$mate -Recurse -Force -ErrorAction SilentlyContinue; git init -q --bare -b develop $remote; git init -q -b develop $s; git -C $s config user.name Practice; git -C $s config user.email practice@example.com; Set-Content "$s/README.md" 'Practice repo'; git -C $s add README.md; git -C $s commit -q -m 'chore: first commit'; git -C $s log --oneline
```

**Spoken script (as in the video):**

> To show the commands themselves safely, I make a small practice repository in the temporary folder, not in the project. I create the develop branch, write a file, run git add, which puts the file in the staging area, then git commit, which saves a snapshot with a message. This is practice, not project history.

**What the output means:** One commit 'chore: first commit' on the practice repository.

**What I will tell the professor:** "git add stages a change, git commit saves it as a snapshot."

## Step 6 - Practice: a feature branch, then stage and commit [video 02:15]

**What I am doing:** running

```powershell
git -C $s switch -c feature/room-search; Add-Content "$s/README.md" 'Room search feature'; git -C $s status --short; git -C $s add README.md; git -C $s status --short; git -C $s commit -q -m 'feat: describe room search'; git -C $s log --oneline
```

**Spoken script (as in the video):**

> Now a feature branch. Git switch with dash c creates feature slash room search and moves me onto it. I edit the file. Git status short shows a space and M: modified but not staged. After git add it shows M in the first column: staged. Then git commit saves it on the feature branch only. Develop is untouched.

**What the output means:** ' M README.md' (modified, not staged), then 'M  README.md' (staged), then two commits on the feature branch.

**What I will tell the professor:** "Work happens on a feature branch; staging then committing records it there only."

## Step 7 - Practice: git push [video 02:42]

**What I am doing:** running

```powershell
git -C $s remote add origin $remote; git -C $s push -u origin feature/room-search; git -C $s branch -vv
```

**Spoken script (as in the video):**

> Git push sends my branch to the remote, the shared copy. In this practice the remote is another local folder, and on a real project it would be GitHub. The dash u option links my local branch to the remote one, so later pushes and pulls know where to go. Git branch dash vv shows that link in square brackets.

**What the output means:** '[new branch] feature/room-search -> feature/room-search', and the branch list showing it tracks origin/feature/room-search.

**What I will tell the professor:** "git push publishes my branch to the shared remote."

## Step 8 - Practice: merge the feature into develop [video 03:06]

**What I am doing:** running

```powershell
git -C $s switch develop; git -C $s merge --no-ff --no-edit feature/room-search; git -C $s log --graph --oneline
```

**Spoken script (as in the video):**

> This is the merge, normally done after a pull request is reviewed. I switch to develop and merge the feature with no fast forward. The graph shows the shape: develop, a side line for the feature, and a merge commit joining them. This is exactly the shape of the real project history we saw earlier.

**What the output means:** 'Merge made by the ort strategy' and a graph with a merge commit joining the feature commit into develop.

**What I will tell the professor:** "Merging with --no-ff creates a visible merge commit for the feature."

## Step 9 - Practice: git pull brings a teammate's work [video 03:29]

**What I am doing:** running

```powershell
git -C $s push -q -u origin develop; git clone -q $remote $mate; git -C $mate config user.name Teammate; git -C $mate config user.email mate@example.com; Add-Content "$mate/README.md" 'Teammate edit'; git -C $mate commit -q -am 'docs: teammate edit'; git -C $mate push -q; git -C $s pull
```

**Spoken script (as in the video):**

> Git pull is the opposite of push: it brings other people's commits to my copy. I push develop, then a second clone, a pretend teammate, makes a commit and pushes it. Now in my repository I run git pull. It fetches the new commit and fast forwards develop to it. Teams run pull often so they work on the latest code.

**What the output means:** 'Updating ... Fast-forward' and 'README.md | 1 +', meaning my develop received the teammate's commit.

**What I will tell the professor:** "git pull downloads and applies teammates' commits to my branch."

## Step 10 - Pull requests and code review: the honest status [video 03:55]

**What I am doing:** running

```powershell
Get-Content docs/pull-requests/feature-security-hardening.md | Select-Object -First 15; 'Pull requests on GitHub: ' + (Invoke-RestMethod 'https://api.github.com/repos/KemNxts/hotel-room-booking-cicd/pulls?state=all').Count
```

**Spoken script (as in the video):**

> A pull request asks the team to review a branch before it is merged. Our prepared pull request text for security hardening has a summary, how it was tested, and an author checklist, and the reviewer checks a second list. But I must be honest. This live query to GitHub shows zero pull requests. Our features were reviewed with this checklist and merged locally. Opening real pull requests on GitHub is a remaining step that needs my GitHub login.

**What the output means:** The prepared PR description (summary, tests, checklist) and then 'Pull requests on GitHub: 0'.

**What I will tell the professor:** "The review checklist was used and the PR texts are ready, but no pull request has been opened on GitHub yet."

## Step 11 - Clean up and confirm the project is untouched [video 04:29]

**What I am doing:** running

```powershell
Remove-Item $s,$remote,$mate -Recurse -Force; 'practice folder exists: ' + (Test-Path $s); git status --short --branch
```

**Spoken script (as in the video):**

> Last, I delete the three practice folders and confirm that my real project repository is unchanged: same branch, and no changes except this demonstration folder. The practice never touched the project history.

**What the output means:** 'practice folder exists: False' and the project's own branch with only the untracked demonstrations folder listed.

**What I will tell the professor:** "The practice repositories are deleted and the project history was never changed."
