# Task 10 - viva questions and answers

**Task 10 - Continuous Testing in Jenkins**

Source: section G of [task-10-continuous-testing-in-jenkins.md](../../task-10-continuous-testing-in-jenkins.md) - answers checked against the
repository and the evidence in this project.

1. **What is a quality gate?** A check that must pass before the pipeline continues - here all lint and tests before Deploy.
2. **How does a failed test stop deployment?** pytest exits non-zero, the
   `sh` step fails, the stage fails and Jenkins skips all later stages.
3. **What defect did you introduce?** `<` became `<=` in the overlap SQL,
   blocking back-to-back stays (check-out day = next check-in day).
4. **Which test caught it?** `TestSearchRooms::test_overlap_rules[2030-01-08-2030-01-10-True]` - a stay ending on the 10th must not block one starting on the 10th.
5. **How do you know it wasn't deployed?** The log shows Deploy skipped, and
   staging's `/health` still reported the previous commit `64351fe`.
6. **Why on an experiment branch?** So the defect never reaches `develop` or
   `main`; `git branch --contains 5844eec` lists only experiment branches.
7. **(Project-specific) What was the stale-report problem?** Build #2's
   report showed 5 E2E tests passing although that stage never ran - an old
   XML file in the reused workspace. Fixed by deleting `reports/` and `dist/` at checkout; build #9 proves it.
8. **(Project-specific) Why do the IDs in Jenkins (`554cad3`) differ from Git (`5844eec`)?**
   Commit messages were edited once before publishing, which changed all IDs;
   see `docs/evidence/git/commit-id-map.md`.
9. **Build failure vs deployment failure?** Build failure: stopped before
   deploying (users unaffected). Deployment failure: the new version started
   but is unhealthy - caught by `--wait` and the health check, fixed by rollback.
10. **Do Selenium tests also gate the deploy?** Yes - the E2E stage comes before Package/Deploy.
11. **Why publish reports even when the build fails?** `post { always }` runs
    on failure too, so you can see *which* test failed.

## Extra questions that match this demonstration

1. **Did you break the stable application to demonstrate this?**
   No. The defect lives only on the throw-away branches experiment/defect-demo and experiment/defect-demo-2, which were never merged into develop or main (git branch --contains proves it). In this video it is reproduced only inside a disposable clone that is deleted afterwards.

2. **Why did Jenkins show 5 passed Selenium tests for a build whose Selenium stage was skipped?**
   That was a real bug found from the evidence: Jenkins reuses its workspace, so reports/e2e-tests.xml from the previous build was still there and was published again. It was fixed by running rm -rf reports dist at the start of every build. Build #9 proves it: it failed on the same test, and its report lists only the tests that actually ran.

3. **How do you know that staging kept running the previous version while build #2 failed?**
   Build #2's Deploy stage never ran (Jenkins logs 'Stage Deploy skipped due to earlier failure(s)'), so nothing touched the staging containers. The last deployment record before it, build #1, says staging ran 1.0.0-64351fe, and the next deployment record, build #3, says 1.0.0-30c6a05, the corrected version.
