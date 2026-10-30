# Task 1 - narration script

**Task 1 - Problem Definition and Scope**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

## Step 1 - Where the Task 1 document lives [video 00:01]

**What I am doing:** running

```powershell
Get-ChildItem docs -Filter 0*.md | Select-Object Name, Length
```

**Spoken script (as in the video):**

> Welcome. This is Task 1, problem definition and scope. Before writing any code, a project must say what problem it solves and when it counts as finished. That agreement is written in one document inside the project's docs folder. I am listing the numbered documents. The first one, zero one, is our Task 1 document, and it is kept in Git like code.

**What the output means:** The docs folder holds numbered documents, one per area; 01 is Task 1. Git history proves it is version-controlled.

**What I will tell the professor:** "Our scope is written down and kept in Git, so every change to it is tracked."

## Step 2 - Problem statement [video 00:29]

**What I am doing:** running

```powershell
Get-Content docs/01-problem-definition.md | Select-Object -Skip 2 -First 12
```

**Spoken script (as in the video):**

> I am opening the problem statement. A small hotel with six rooms takes bookings by phone and spreadsheet. Guests cannot see free rooms, and sometimes two people get the same room for the same night. That is the business problem. The second paragraph is the DevOps problem: changes must reach guests quickly without breaking bookings, so we replace manual copying and testing with an automated pipeline.

**What the output means:** The first paragraph is the business problem (manual bookings, double bookings); the second is the DevOps problem (unsafe manual releases).

**What I will tell the professor:** "The project solves two problems: guests cannot self-book, and releases were manual and untested."

## Step 3 - Target users and stakeholders [video 00:59]

**What I am doing:** running

```powershell
Get-Content docs/01-problem-definition.md | Select-Object -Skip 15 -First 18
```

**Spoken script (as in the video):**

> Target users are the people who use the system directly: the guest, the developer and the operator. Stakeholders are everyone affected by it, such as the hotel owner and the front desk. Each wants something different. The owner wants no double bookings, the operator wants safe deployments. Please note that these are a reasoned model of a small hotel. We did not interview real hotel staff.

**What the output means:** Users use the system; stakeholders are affected by it. Each group wants something different.

**What I will tell the professor:** "We identified who uses and who cares about the system, and we are honest that no real interviews were done."

## Step 4 - Pain points and objectives [video 01:29]

**What I am doing:** running

```powershell
Get-Content docs/01-problem-definition.md | Select-Object -Skip 34 -First 21
```

**Spoken script (as in the video):**

> These are the six existing pain points, from double bookings to having no rollback after a bad release. Each objective, O1 to O7, answers them. For example O2 says overlapping bookings must be impossible, both in code and in the database, and O4 says a failing test must block deployment automatically.

**What the output means:** Six pain points map to seven objectives O1 to O7. O2 (no overlap) and O4 (failing test blocks deploy) are the key ones.

**What I will tell the professor:** "Every pain point has an objective that answers it."

## Step 5 - Constraints [video 01:54]

**What I am doing:** running

```powershell
Get-Content docs/01-problem-definition.md | Select-Object -Skip 55 -First 19
```

**Spoken script (as in the video):**

> Constraints are the limits we work within. Technically we use Python, Flask and SQLite, which allows one writer at a time. Operationally we have a ten day schedule, no paid cloud, and no public server, so Jenkins polls Git instead of using a webhook. Stating constraints early explains design choices later.

**What the output means:** Constraints explain design choices: SQLite means one writer, no public server means Jenkins polls Git.

**What I will tell the professor:** "Our limits were stated up front, and they explain why the design looks the way it does."

## Step 6 - Measurable success criteria [video 02:20]

**What I am doing:** running

```powershell
Get-Content docs/01-problem-definition.md | Select-Object -Skip 74 -First 13
```

**Spoken script (as in the video):**

> Success criteria are targets you can check with a number or a yes or no. The left column is the target, the right column is the evidence we achieved it. For example, at least fifty automated tests all passing, and a repeat Ansible run that changes nothing. Saying it works well cannot be proven. Ninety of ninety tests passing can.

**What the output means:** Each row has a target and the evidence that it was achieved, e.g. 90 tests, changed=0 on repeat Ansible run.

**What I will tell the professor:** "Success is measured with numbers I can show you, not opinions."

## Step 7 - Proving one criterion live: the automated tests [video 02:48]

**What I am doing:** running

```powershell
pytest -q -m "not e2e"
```

**Spoken script (as in the video):**

> Let me prove one criterion live instead of just reading it. I am running the project's automated tests, without the browser tests. If every test passes, the criterion that the tests must all pass is met right now, not only on the day the document was written. This takes about twenty seconds.

**What the output means:** pytest prints one dot per passing test and a summary line such as '85 passed, 5 deselected'. Deselected are the 5 browser tests that this command skips.

**What I will tell the professor:** "The criterion that all automated tests pass is true right now, not only on the day we wrote it."

## Step 8 - Approved MVP scope [video 03:11]

**What I am doing:** running

```powershell
Get-Content docs/01-problem-definition.md | Select-Object -Skip 87 -First 17
```

**Spoken script (as in the video):**

> Finally the scope. MVP means Minimum Viable Product, the smallest version that is genuinely useful. Ours is six booking workflows: register and log in, check availability by date, request, confirm, cancel, and track a booking. Payments, an admin screen and e-mails are deliberately out of scope, so the project stays finishable. What I tell the professor: the problem is clear, the scope is fixed, and success is measured.

**What the output means:** The MVP is the 6 workflows; payments, admin UI and e-mail are listed as out of scope on purpose.

**What I will tell the professor:** "The scope is fixed at six workflows, which is what makes the project finishable and checkable."
