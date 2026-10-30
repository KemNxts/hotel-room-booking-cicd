# Task 5 - viva questions and answers

**Task 5 - Feature Development with Branching**

Source: section G of [task-05-feature-development-and-branching.md](../../task-05-feature-development-and-branching.md) - answers checked against the
repository and the evidence in this project.

1. **Why use feature branches?** Unfinished work stays out of `develop`, so
   develop always builds and passes tests; several features can progress in parallel.
2. **What is a pull request?** A GitHub page that asks to merge one branch
   into another, where the change is reviewed and discussed first.
3. **Did you create pull requests?** Not on GitHub - GitHub shows 0 PRs. I
   merged locally with `--no-ff` and pushed; the review records are in
   `docs/pull-requests/`. Creating real PRs is my remaining step.
4. **What does `--no-ff` do?** Always creates a merge commit, so a feature's
   commits stay grouped in the history.
5. **`git pull` vs `git fetch`?** `fetch` downloads new commits; `pull` = fetch + merge into your current branch.
6. **(Project-specific) Show a feature branch and its commits.**
   `feature/security-hardening`: `716b910 feat: add CSRF protection...` and
   `fd3cb60 test: add route-level integration tests...`, merged as `bdfc2fb`.
7. **(Project-specific) What does your review checklist check?** No SQL
   outside DAOs, server-side validation, booking ownership, CSRF token on new
   forms, and that tests would fail if the code were broken.
8. **How did you test the feature before merging?** `flake8` and the full
   pytest suite locally; after merging, Jenkins built `develop`.
9. **What would a reviewer comment look like?** A note on a specific line,
   e.g. "this route changes data - does the form include `csrf_token`?" (an
   example - no real comments exist yet).
10. **What if two features change the same lines?** A merge conflict - see
    Task 6, where exactly that happened and was resolved.

## Extra questions that match this demonstration

1. **The project documents quote commit IDs that do not match `git log` today. Why?**
   On 12 October 2026 the history was rewritten once to remove automated co-author lines from commit messages, so every commit ID changed. The old-to-new map is in docs/evidence/git/commit-id-map.md. Branch names and commit messages are unchanged, so in a demo I use branch names and live git commands.

2. **Do GitHub pull requests exist for these features?**
   No. The features were merged locally with git merge --no-ff after a checklist review, and the pull request texts are prepared in docs/pull-requests/. The live check shows 0 pull requests on GitHub. Opening real pull requests needs the student's GitHub login.
