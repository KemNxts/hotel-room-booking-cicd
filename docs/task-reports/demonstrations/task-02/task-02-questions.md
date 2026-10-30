# Task 2 - viva questions and answers

**Task 2 - Agile Planning and DevOps Workflow**

Source: section G of [task-02-agile-planning-and-devops-workflow.md](../../task-02-agile-planning-and-devops-workflow.md) - answers checked against the
repository and the evidence in this project.

1. **What is a user story?** A short requirement from the user's viewpoint:
   "As a <user> I want <goal> so that <reason>."
2. **What are acceptance criteria?** The conditions that make a story
   accepted. Ours are checked automatically by named tests.
3. **Difference between a backlog and a sprint?** The backlog is the whole
   ordered to-do list; a sprint is a short time-box in which a chosen part of
   the backlog is completed.
4. **Kanban or Scrum - which did you use?** A light mix: a Kanban board to
   show status and three short Scrum-style sprints with a review each.
5. **What is your Definition of Done?** Branch + conventional commits, tests,
   flake8 clean, all tests pass, Jenkins green, `--no-ff` merge with the PR
   checklist, docs updated, no secrets.
6. **How is the DoD enforced, not just written?** Jenkins runs flake8 and all
   90 tests; deployment happens only if they pass (shown by failed build #2).
7. **(Project-specific) Where are your GitHub issues?** None exist yet
   (0 issues on GitHub). The backlog is in `docs/02-agile-plan.md`; creating
   the issues needs my GitHub account and is the remaining step.
8. **(Project-specific) Which story covers rollback and how is it proven?**
   US9; proven by `deploy/ansible/rollback.yml` runs where `/health` showed
   1.0.0 again and 5/5 Selenium journeys passed.
9. **What does the DevOps lifecycle diagram show that a simple list does not?**
   The feedback loops: failed tests go back to Code, and problems in
   operation lead to rollback and new planning.
10. **What happened in your sprint retrospective?** Two features built in
    parallel (two footers) caused a merge conflict; the lesson was to agree on
    shared files earlier. The conflict and its resolution are documented.

## Extra questions that match this demonstration

1. **Do GitHub issues exist for the backlog?**
   No. The backlog is written in docs/02-agile-plan.md and the issue templates are ready, but no GitHub issues have been created yet (the live check in this video shows 0). Creating one issue per HB item is the remaining step and needs the student's GitHub login.
