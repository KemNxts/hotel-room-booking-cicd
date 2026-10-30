# Task 6 - viva questions and answers

**Task 6 - MVP Completion and Git Collaboration**

Source: section G of [task-06-mvp-completion-and-collaboration.md](../../task-06-mvp-completion-and-collaboration.md) - answers checked against the
repository and the evidence in this project.

1. **What is a merge conflict?** Two branches changed the same lines; Git cannot choose, so a human edits the result.
2. **How did your conflict happen?** Two features branched from the same
   commit and both added a footer in `base.html` (plus CSS and a test). The second merge conflicted in all three files.
3. **How did you resolve it?** Kept both features (contact line, then release
   line), merged the CSS into one rule, kept both tests, ran flake8 and all
   tests (89 passed), then committed the merge `9e766ac`.
4. **How do you know you didn't break anything?** Tests after resolution, and
   Jenkins build #4 of develop was green before the v1.0.0 release.
5. **Branch vs tag?** A branch moves with new commits; a tag stays on one commit.
6. **Why tag releases?** To redeploy or roll back exactly what was released
   (`v1.0.0` was used for the Ansible rollback demo).
7. **(Project-specific) How are passwords stored?** Werkzeug scrypt hashes
   (`generate_password_hash`), never plain text - a unit test checks this.
8. **(Project-specific) What stops one guest cancelling another's booking?**
   The service checks the owner; another user gets 404 and the status stays unchanged (integration test).
9. **What is a stable baseline?** A tagged commit on `main` that passed the
   full pipeline - `v1.1.0` (`ce1726d`), running in prod.
10. **Why are there two IDs for the same commit in your documents?** The
    messages were edited once before publishing (removing a co-author line);
    the map is in `docs/evidence/git/commit-id-map.md`.
11. **Is the conflict screenshot genuine?** Yes - Git's own output was saved
    to a file at the time, and the conflict can be reproduced live from the
    pushed branches, as in the demo.

## Extra questions that match this demonstration

1. **Did you use your real database in this demonstration?**
   No. The recorder starts the real application against a temporary database file, so no real guest data is created or changed. The code and pages are the real application.

2. **Is this conflict real or staged?**
   It is real. Two feature branches were created from the same develop commit and both added a footer in the same lines of base.html, style.css and a test file. Git could not merge them automatically. The original terminal output was saved in docs/evidence/git/merge-conflict.txt, and in the video the same conflict is reproduced live in a throw-away clone with identical results.

3. **Why do the commit IDs in docs/evidence differ from the IDs I see now?**
   The history was rewritten once (12 October 2026) to remove automated co-author lines, so IDs changed; evidence files keep the original IDs and docs/evidence/git/commit-id-map.md maps old to new.
