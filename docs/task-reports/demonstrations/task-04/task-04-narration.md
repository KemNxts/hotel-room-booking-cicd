# Task 4 - narration script

**Task 4 - Git and GitHub Repository Initialization**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

## Step 1 - The repository and its key files [video 00:01]

**What I am doing:** running

```powershell
Get-ChildItem -Force -Name | Select-String '^(README|CONTRIBUTING|VERSION|\.git)'
```

**Spoken script (as in the video):**

> This is Task 4, Git and GitHub repository initialization. A repository is the project folder plus its complete history, stored in a hidden dot git folder. Here I list the Git related items in the project root: the dot git folder, the dot github folder, dot gitattributes, dot gitignore, CONTRIBUTING, README and a VERSION file. Each one has a purpose, and I will open them.

**What the output means:** .git (the history), .github (templates), .gitattributes, .gitignore, CONTRIBUTING.md, README.md, VERSION.

**What I will tell the professor:** "The repository contains the standard project files that every team repository should have."

## Step 2 - README: the front page [video 00:31]

**What I am doing:** running

```powershell
Get-Content README.md | Select-Object -First 14
```

**Spoken script (as in the video):**

> The README is the front page of the project. It says what the project is, what the features are, and links to the documentation. Anyone who opens the repository on GitHub reads this first. It also contains the commands to run and test the application.

**What the output means:** Project title, a one paragraph description, the current release in the VERSION file, and pointers to the project report and the 15-task checklist.

**What I will tell the professor:** "The README explains the project and where to find everything."

## Step 3 - .gitignore: what Git must not store [video 00:51]

**What I am doing:** running

```powershell
(Get-Content .gitignore | Select-String -NotMatch '^\s*(#|$)') -join '  '; git check-ignore -v deploy/jenkins/.env instance/hotel.db .venv
```

**Spoken script (as in the video):**

> The dot gitignore file lists files that Git must never store: the virtual environment, the database, test reports, environment files with passwords, and certificates. Here are the real rules. Then I ask Git itself, with check ignore, why three files are ignored. It names the rule and the line number. That is how secrets like the Jenkins password file stay out of the repository.

**What the output means:** The list of ignore patterns, then three lines of the form '.gitignore:27:.env   deploy/jenkins/.env', showing the rule that ignores each file.

**What I will tell the professor:** "Passwords, databases and virtual environments are excluded from the repository by rule."

## Step 4 - .gitattributes: line endings [video 01:23]

**What I am doing:** running

```powershell
Get-Content .gitattributes
```

**Spoken script (as in the video):**

> The dot gitattributes file tells Git how to treat text files. Windows uses a different line ending than Linux. The first rule stores everything with Linux line endings in the repository. That matters because our Dockerfiles, Ansible files and scripts run inside Linux containers, and Windows line endings would break them.

**What the output means:** '* text=auto eol=lf' stores LF line endings; .bat and .ps1 keep CRLF; images are marked binary.

**What I will tell the professor:** "Line endings are fixed by rule so files written on Windows still work inside Linux containers."

## Step 5 - CONTRIBUTING: the team rules [video 01:48]

**What I am doing:** running

```powershell
Get-Content CONTRIBUTING.md | Select-Object -First 24
```

**Spoken script (as in the video):**

> CONTRIBUTING documents the team conventions. Main holds released code. Develop is where features meet and are tested together. Every change is made on its own feature branch, cut from develop. Branch names are lowercase with hyphens, and experiment branches are never merged. Writing the rules down means everyone works the same way.

**What the output means:** A table of branches (main, develop, feature/*) with their purpose and who merges into them, followed by the naming rules.

**What I will tell the professor:** "The branching rules and commit conventions are documented in CONTRIBUTING."

## Step 6 - Issue templates [video 02:14]

**What I am doing:** running

```powershell
Get-ChildItem .github -Recurse -File | Resolve-Path -Relative; Get-Content .github/ISSUE_TEMPLATE/feature_request.md
```

**Spoken script (as in the video):**

> These are the issue templates in the dot github folder. A bug report template and a feature request template give every issue the same structure: what happened, what was expected, and acceptance criteria. GitHub shows them automatically when someone clicks New issue.

**What the output means:** Three template files, then the content of the feature request template.

**What I will tell the professor:** "Templates for issues and pull requests are ready so everyone reports in the same format."

## Step 7 - Pull request template and review checklist [video 02:35]

**What I am doing:** running

```powershell
Get-Content .github/pull_request_template.md | Select-Object -First 22
```

**Spoken script (as in the video):**

> This is the pull request template. When a developer opens a pull request, GitHub pre fills this text. It asks what the change does and how it was tested, and gives an author checklist: branch name, commit message, linter clean, tests passing, Jenkins green and no secrets. A reviewer has a second checklist below. This is what supports code review.

**What the output means:** Sections: What does this PR do, How was it tested, and the author checklist with seven boxes.

**What I will tell the professor:** "Every change goes through a checklist before it is merged."

## Step 8 - Branches that exist today [video 03:04]

**What I am doing:** running

```powershell
git status --short --branch; git branch
```

**Spoken script (as in the video):**

> Now the real repository. Git status shows the current branch and whether anything is changed. A branch is a separate line of development. Below is the list of all local branches: main for releases, develop for integration, many feature branches, fix branches, and two experiment branches. The star marks the branch I am on now.

**What the output means:** The current branch with a star, then 20 local branches: main, develop, feature/*, fix/*, experiment/*, docs/*. Untracked files in the demonstrations folder are this recording work.

**What I will tell the professor:** "Every feature has its own branch; main and develop are the long-lived ones."

## Step 9 - History as a graph [video 03:31]

**What I am doing:** running

```powershell
git log --oneline --graph --decorate -20
```

**Spoken script (as in the video):**

> The log graph shows the history. Each line is a commit, a saved snapshot with a message. The lines with a slash show a feature branch splitting from develop and merging back. The names in brackets are branches. Each feature, such as nights column or ansible rollback, is visible as a unit because we merged with no fast forward.

**What the output means:** A graph of commits; merge commits named 'Merge branch feature/... into develop', each with the feature's own commits beside it.

**What I will tell the professor:** "The history shows each feature as its own branch merged into develop."

## Step 10 - Tags and the remote [video 03:58]

**What I am doing:** running

```powershell
git tag -n1; git remote -v
```

**Spoken script (as in the video):**

> A tag is a permanent label on one commit, used for releases. We have version 1.0.0 and 1.1.0. A branch moves forward as you commit, a tag stays put. A remote is another copy of the repository on a server. Ours is called origin and points to GitHub. The address contains no password.

**What the output means:** Two tags with their messages, and origin fetch/push URLs of the public GitHub repository.

**What I will tell the professor:** "Releases are tagged and the remote copy lives on GitHub."

## Step 11 - Local repository versus the GitHub repository [video 04:25]

**What I am doing:** running

```powershell
$u = 'https://api.github.com/repos/KemNxts/hotel-room-booking-cicd'; $r = Invoke-RestMethod $u; "$($r.full_name)  public=$(-not $r.private)  default=$($r.default_branch)"; "branches on GitHub: $((Invoke-RestMethod "$u/branches?per_page=100").Count)"; 'tags on GitHub: ' + ((Invoke-RestMethod "$u/tags").name -join ', '); git log --oneline -1 develop; git log --oneline -1 origin/develop
```

**Spoken script (as in the video):**

> Local and remote are different things. My local repository is on this laptop. The remote is on GitHub. So I ask GitHub directly. It confirms a public repository, with nineteen branches and both release tags, and the develop branch is at the same commit locally and on GitHub. Issues and pull requests do not exist yet, only their templates and prepared texts.

**What the output means:** KemNxts/hotel-room-booking-cicd public=True default=main; 19 branches; tags v1.1.0, v1.0.0; the same commit id for develop and origin/develop.

**What I will tell the professor:** "The project is on GitHub with all branches and tags; the remaining GitHub work is issues and pull requests."

## Step 12 - Anatomy of one commit [video 04:56]

**What I am doing:** running

```powershell
git show --stat --format='commit %h%nAuthor: %an%nDate:   %ad%n%n    %s' --date=short feature/nights-column
```

**Spoken script (as in the video):**

> Finally, one commit in detail. It has an identifier, an author, a date and a message that follows our convention: type, colon, short description. Here feat means a new feature. The statistics show exactly which files changed, here the my bookings template and a test. Small, focused commits make review and rollback easy.

**What the output means:** Commit 2d67e39 'feat: show number of nights in the My bookings list' changing a template and a test file (10 insertions, 1 deletion).

**What I will tell the professor:** "A commit is a small, labelled snapshot that shows exactly what changed and why."
