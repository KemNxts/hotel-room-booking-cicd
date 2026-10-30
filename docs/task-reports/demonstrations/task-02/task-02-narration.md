# Task 2 - narration script

**Task 2 - Agile Planning and DevOps Workflow**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

## Step 1 - What the Agile plan document contains [video 00:01]

**What I am doing:** running

```powershell
Select-String -Path docs/02-agile-plan.md -Pattern '^## ' | Select-Object LineNumber, Line
```

**Spoken script (as in the video):**

> This is Task 2, Agile planning and the DevOps workflow. Agile means we build in small steps and keep a list of work to do. I am listing the headings of the planning document. It has user stories, a product backlog, a Kanban board, a sprint plan, the Definition of Done, and the DevOps lifecycle diagram. I will walk through each one.

**What the output means:** Six headings with their line numbers: stories, backlog, Kanban board, sprint plan, Definition of Done, lifecycle.

**What I will tell the professor:** "The planning is written in one versioned document with everything an Agile team needs."

## Step 2 - User stories [video 00:28]

**What I am doing:** running

```powershell
Select-String -Path docs/02-agile-plan.md -Pattern '^\| US' | ForEach-Object { ($_.Line -split '\|')[1,2] -join ' ->' }
```

**Spoken script (as in the video):**

> A user story is one sentence that says who wants what and why, in the form: as a guest, I want something, so that something. Stories one to six are the six booking features. Stories seven to nine are for the developer and the operator: automatic testing, one command deployment, and rollback. Writing needs as stories keeps every feature tied to a real person.

**What the output means:** Nine stories, US1 to US9, each as 'As a ... I want ...'.

**What I will tell the professor:** "Every feature is written as a user story, so each one has a person and a reason."

## Step 3 - Acceptance criteria [video 00:56]

**What I am doing:** running

```powershell
(Select-String -Path docs/02-agile-plan.md -Pattern '^\| US5').Line
```

**Spoken script (as in the video):**

> Acceptance criteria say exactly when a story is finished. Here is story five, cancelling a booking. A pending or confirmed booking becomes cancelled, the room becomes free, and you cannot cancel twice. Notice that the last part names the automated tests that check it. So the criteria are not opinions, they are tests.

**What the output means:** One table row: story US5 with its criteria and the test names TestCancelBooking and test_journey_4.

**What I will tell the professor:** "Each acceptance criterion is linked to an automated test, so completion can be checked by running it."

## Step 4 - Proving story 5 with its tests, live [video 01:22]

**What I am doing:** running

```powershell
pytest tests/unit/test_booking_service.py -k cancel -v --no-header
```

**Spoken script (as in the video):**

> Now I prove story five live. I run only the tests whose name contains cancel. Seven tests run and seven should pass, including cannot cancel twice and other user cannot cancel. If these pass, the acceptance criteria of the cancellation story are met today.

**What the output means:** 7 passed, 31 deselected. Each line is one test name with PASSED; 'deselected' means other tests were skipped on purpose.

**What I will tell the professor:** "I can prove an acceptance criterion in seconds by running its tests."

## Step 5 - Product backlog [video 01:44]

**What I am doing:** running

```powershell
Select-String -Path docs/02-agile-plan.md -Pattern '^\| HB-' | ForEach-Object { ($_.Line -split '\|')[1,2,3,5] -join ' |' }
```

**Spoken script (as in the video):**

> The product backlog is the ordered list of work. Our backlog items are HB one to HB fifteen, one for each of the fifteen course tasks, with the task number and a status. All are done. Items like payments are not here, because they are out of scope.

**What the output means:** Fifteen rows HB-01 to HB-15, each with its course task number and status Done.

**What I will tell the professor:** "The fifteen course tasks are the backlog; each item has a status."

## Step 6 - GitHub issues: the honest status [video 02:05]

**What I am doing:** running

```powershell
$r = Invoke-RestMethod https://api.github.com/repos/KemNxts/hotel-room-booking-cicd; "open issues on GitHub: $($r.open_issues_count)"; Get-ChildItem .github -Recurse -File | Resolve-Path -Relative
```

**Spoken script (as in the video):**

> I want to be honest about GitHub issues. This command asks GitHub, live, how many issues the public repository has. The answer is zero. The backlog exists in the document, and the issue and pull request templates are ready in the dot github folder, but the real GitHub issues have not been created yet. That is the one remaining step for this task.

**What the output means:** 'open issues on GitHub: 0', then the three template files: bug report, feature request and pull request template.

**What I will tell the professor:** "The backlog is in the repository and the templates are ready, but I have not yet created GitHub issues."

## Step 7 - Kanban board [video 02:33]

**What I am doing:** running

```powershell
Get-Content docs/02-agile-plan.md | Select-Object -Skip 41 -First 12
```

**Spoken script (as in the video):**

> A Kanban board shows work moving through columns: backlog, to do, in progress, review and done. Each card moved from left to right. A card reached review when its feature branch was ready to merge, and done when it met the Definition of Done. Payments and an admin screen stay in the backlog as future work.

**What the output means:** A five-column table; HB-01 to HB-15 are in Done; payments, admin UI and auto-expiry stay in Backlog.

**What I will tell the professor:** "The board shows every item finished and the out-of-scope ideas parked in the backlog."

## Step 8 - Sprint plan [video 02:58]

**What I am doing:** running

```powershell
Get-Content docs/02-agile-plan.md | Select-Object -Skip 53 -First 13
```

**Spoken script (as in the video):**

> A sprint is a short fixed period of work with a goal. We planned three sprints in ten working days. Sprint one is foundation, sprint two is automation with Jenkins and Docker, and sprint three is operations and release. Each sprint ends with a review, a demo of what works, and a retrospective, what to keep and what to improve.

**What the output means:** Three sprints with days, goals and the backlog items in each; a note about the footer branches that conflicted and how that was fixed.

**What I will tell the professor:** "Work was organised into three goal-based sprints that each ended with a review and a retrospective."

## Step 9 - Definition of Done [video 03:23]

**What I am doing:** running

```powershell
Get-Content docs/02-agile-plan.md | Select-Object -Skip 66 -First 12
```

**Spoken script (as in the video):**

> The Definition of Done is the checklist that must be true before any item counts as finished. Code on a feature branch, automated tests, a clean linter, a green Jenkins pipeline, a merge into develop, updated documentation and no secrets. This is how completion is determined, so nobody can say it is done when it is not.

**What the output means:** Seven numbered conditions. Items 3 and 4 are enforced automatically by Jenkins.

**What I will tell the professor:** "An item is done only when all seven conditions are met, and the pipeline checks the important ones for me."

## Step 10 - DevOps lifecycle diagram [video 03:49]

**What I am doing:** running

```powershell
Get-Content docs/02-agile-plan.md | Select-Object -Skip 79
```

**Spoken script (as in the video):**

> This is the DevOps lifecycle, written as a diagram in text form. It is drawn automatically on GitHub. Plan, code, build, test. If any test fails we stop and fix, there is no deployment. If everything is green we release, deploy, operate and monitor, and if there is a problem we roll back to the previous version, and then planning starts again.

**What the output means:** Mermaid diagram source: boxes Plan, Code, Build, Test, Release, Deploy, Operate, Monitor, Rollback, with an arrow that stops the flow when a test fails.

**What I will tell the professor:** "A change travels from plan to monitoring automatically, and a failed test stops it before deployment."

## Step 11 - The lifecycle in the real pipeline [video 04:19]

**What I am doing:** running

```powershell
Select-String -Path Jenkinsfile -Pattern "stage\('" | ForEach-Object { $_.Line.Trim() }
```

**Spoken script (as in the video):**

> Finally, here is the same workflow in real code. These are the stages in our Jenkinsfile, in order: checkout, install, static checks, tests, Selenium browser tests, package, build images, publish, deploy and health check. A developer's code change passes through them one after another. Only if the test stages pass does the pipeline reach deployment. That is how a task is traced from commit to operation.

**What the output means:** Ten stage names. Test stages come before Package, Build, Publish and Deploy, which is the quality gate.

**What I will tell the professor:** "The lifecycle diagram is not just a picture; the Jenkinsfile implements it stage by stage."
