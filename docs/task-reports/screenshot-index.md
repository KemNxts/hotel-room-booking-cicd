# Screenshot inventory

Generated from the figure references in the 15 task reports on 2026-10-20. Every file listed as *verified* exists on disk. "Browser screenshot" = captured from the running system or GitHub with headless Chrome; "rendered from real output" = a real command or log rendered as an image by `scripts/capture_report_evidence.py` (the raw text is kept next to it or in `assets/raw/`).

**86 referenced screenshots, 0 missing references, 9 still to be captured manually.**

| Task | File | Evidence purpose | Captured | Status |
|---|---|---|---|---|
| 1 | `assets/task-01/github-doc-01-problem-definition.png` | `docs/01-problem-definition.md` as published on the public GitHub repository (captured 2026-10-20). | 2026-10-20 | verified (browser screenshot) |
| 2 | `assets/task-02/github-doc-02-agile-plan.png` | `docs/02-agile-plan.md` on GitHub (captured 2026-10-20). | 2026-10-20 | verified (browser screenshot) |
| 2 | `assets/task-02/github-issues-empty.png` | The repository's Issues page (all states) shows no issues (captured 2026-10-20). | 2026-10-20 | verified (browser screenshot) |
| 3 | `assets/task-03/github-doc-03-srs-architecture.png` | `docs/03-srs-architecture.md` on GitHub with diagrams rendered (captured 2026-10-20). | 2026-10-20 | verified (browser screenshot) |
| 3 | `assets/task-03/flask-routes.png` | `python -m flask --app wsgi routes` run on 2026-10-20 (rendered from real output). | 2026-10-20 | verified (rendered from real command/log output) |
| 3 | `assets/task-03/project-structure.png` | Files under `app/` and `tests/` (from `git ls-files`, rendered from real output). | 2026-10-20 | verified (rendered from real command/log output) |
| 3 | `assets/task-03/github-file-app_schema.sql.png` | `app/schema.sql` on GitHub. | 2026-10-20 | verified (browser screenshot) |
| 3 | `assets/task-03/app-desktop-01-home.png` | Figure 3.5 - The running application | 2026-10-20 | verified (browser screenshot) |
| 4 | `assets/task-04/git-branches-tags-remote.png` | `git branch -a`, `git tag -n1`, `git remote -v` (rendered from real output, 2026-10-20). | 2026-10-20 | verified (rendered from real command/log output) |
| 4 | `assets/task-04/git-main-history.png` | Main-branch history and the skeleton commit `541dad5` with its files (rendered from real output). | 2026-10-20 | verified (rendered from real command/log output) |
| 4 | `assets/task-04/gitignore-and-templates.png` | `.github` templates, `.gitattributes` and `.gitignore` (rendered from real output). | 2026-10-20 | verified (rendered from real command/log output) |
| 4 | `assets/task-04/github-repository-home.png` | The public GitHub repository home page (captured 2026-10-20). | 2026-10-20 | verified (browser screenshot) |
| 4 | `assets/task-04/github-branches.png` | All branches on GitHub. | 2026-10-20 | verified (browser screenshot) |
| 4 | `assets/task-04/github-templates-folder.png` | `.github/` on GitHub: `ISSUE_TEMPLATE/` and `pull_request_template.md`. | 2026-10-20 | verified (browser screenshot) |
| 5 | `assets/task-05/feature-branch-history.png` | `git log --graph` of `feature/security-hardening` and `git show --stat 716b910` (rendered from real output, 2026-10-20). | 2026-10-20 | verified (rendered from real command/log output) |
| 5 | `assets/task-05/all-feature-merges.png` | `git log --merges --first-parent develop` (rendered from real output). | 2026-10-20 | verified (rendered from real command/log output) |
| 5 | `assets/task-05/github-compare-merged-into-develop.png` | GitHub compare `develop...feature/nights-column` (captured 2026-10-20). | 2026-10-20 | verified (browser screenshot) |
| 5 | `assets/task-05/github-pull-requests-empty.png` | The repository's Pull requests page (all states): none. | 2026-10-20 | verified (browser screenshot) |
| 5 | `assets/task-05/github-compare-feature-changes.png` | GitHub compare from the branch's starting point `a2bb052` to `feature/nights-column`. | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/app-desktop-03-register.png` | Workflow 1: registration form with labelled fields and the password rule. | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/app-desktop-05-login-error.png` | Workflow 1: login with wrong credentials shows a neutral error (does not reveal which part was wrong). | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/app-desktop-06-availability-logged-in.png` | Workflow 2: availability for the chosen dates - booked rooms marked "Booked", free rooms with the total for the stay. | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/app-desktop-08-booking-requested.png` | Workflow 3: the new booking is PENDING. | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/app-desktop-09-booking-confirmed.png` | Workflow 4: CONFIRMED, progress shows both steps done. | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/app-desktop-10-cancel-dialog.png` | Workflow 5: cancelling opens a confirmation dialog first. | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/app-desktop-11-booking-cancelled.png` | Workflow 5: status CANCELLED, room released. | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/app-desktop-12-my-bookings.png` | Workflow 6: status tracking for all of the guest's bookings (PENDING, CANCELLED, CONFIRMED). | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/app-mobile-12-my-bookings.png` | The same page at phone width (375 px). | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/merge-conflict-output.png` | The conflict as recorded on 2026-10-11 (rendered from `docs/evidence/git/merge-conflict.txt`; original commit IDs). | 2026-10-20 | verified (rendered from real command/log output) |
| 6 | `assets/task-06/merge-conflict-resolution.png` | `git log --graph` and `git show --stat 9e766ac` today (rendered from real output). | 2026-10-20 | verified (rendered from real command/log output) |
| 6 | `assets/task-06/release-tags.png` | `git tag -n1` and the annotated tag object of `v1.1.0` (rendered from real output). | 2026-10-20 | verified (rendered from real command/log output) |
| 6 | `assets/task-06/github-release-tags.png` | `v1.0.0` and `v1.1.0` on GitHub. | 2026-10-20 | verified (browser screenshot) |
| 6 | `assets/task-06/github-doc-04-git-workflow.png` | `docs/04-git-workflow.md` on GitHub: branching model, merges, the conflict story and the release procedure. | 2026-10-20 | verified (browser screenshot) |
| 7 | `assets/task-07/jenkins-job-stage-view.png` | Job `hotel-booking`: build history #1-#11, test-result trend, last artifacts and the stage view (captured 2026-10-20). | 2026-10-20 | verified (browser screenshot) |
| 7 | `assets/task-07/jenkins-job-configuration.png` | Job configuration: the three parameters, "Do not allow concurrent builds", Poll SCM `H/5 | 2026-10-20 | verified (browser screenshot) |
| 7 | `assets/task-07/jenkins-build-11-summary.png` | Build #11 (`1.1.0-1c2103c`), started 2026-10-20: result SUCCESS. | 2026-10-20 | verified (browser screenshot) |
| 7 | `assets/task-07/jenkins-build-11-tests.png` | Test report of build #11: 90 tests, 0 failures, grouped by package (unit, integration, e2e). | 2026-10-20 | verified (browser screenshot) |
| 7 | `assets/task-07/jenkins-build-11-artifacts.png` | Archived artifacts of build #11: source tarball + `.sha256`, test XML, `health.json`, `deployment.txt`. | 2026-10-20 | verified (browser screenshot) |
| 7 | `assets/task-07/jenkins-files.png` | `deploy/jenkins/plugins.txt` and the running Jenkins + registry containers (rendered from real output, 2026-10-20). | 2026-10-20 | verified (rendered from real command/log output) |
| 8 | `assets/task-08/github-file-Jenkinsfile.png` | `Jenkinsfile` on GitHub (captured 2026-10-20). | 2026-10-20 | verified (browser screenshot) |
| 8 | `assets/task-08/jenkinsfile-stages.png` | Line numbers of every stage and parameter (`findstr` on the Jenkinsfile, rendered from real output). | 2026-10-20 | verified (rendered from real command/log output) |
| 8 | `assets/task-08/jenkins-build-with-parameters.png` | The | 2026-10-20 | verified (browser screenshot) |
| 8 | `assets/task-08/jenkins-build-11-console.png` | Build #11 console excerpt (rendered from the saved console log): each stage starting, 85 + 5 tests passed, the archive checksum, image pushes with digests, `/health` and "Deployed 1.1.0-1c2103c to staging". | 2026-10-20 | verified (rendered from real command/log output) |
| 8 | `assets/task-08/staging-health-after-build-11.png` | http://localhost:8081/health in a browser after build #11: commit `1c2103c`, env `staging`, version `1.1.0`. | 2026-10-20 | verified (browser screenshot) |
| 8 | `assets/task-08/jenkins-credentials-masked.png` |  | 2026-10-20 | verified (browser screenshot) |
| 9 | `assets/task-09/selenium-run.png` | `pytest -m e2e -v` on 2026-10-20 (rendered from real output): 5 journeys PASSED. | 2026-10-20 | verified (rendered from real command/log output) |
| 9 | `assets/task-09/full-test-suite.png` | flake8 (no findings), then unit 59, integration 26 and e2e 5 passed (rendered from real output, 2026-10-20). | 2026-10-20 | verified (rendered from real command/log output) |
| 9 | `assets/task-09/github-file-tests_e2e_test_journeys.py.png` | Figure 9.3 - Journey source on GitHub | 2026-10-20 | verified (browser screenshot) |
| 9 | `assets/task-09/selenium-failure-demo-output.png` | A temporary, deliberately failing test run on 2026-10-20 (rendered from real output): "failure screenshot saved: reports\screenshots\...png", then `1 failed`; the folder contains a `.png` and an `.html`. | 2026-10-20 | verified (rendered from real command/log output) |
| 9 | `assets/task-09/selenium-failure-screenshot-saved-by-hook.png` | The actual image saved by the hook: what the browser showed at the moment of failure. | 2026-10-20 | verified (browser screenshot) |
| 9 | `assets/task-09/app-desktop-07-my-bookings-empty.png` | The empty "My bookings" state (redesigned UI) - one of the pages the journeys navigate. | 2026-10-20 | verified (browser screenshot) |
| 10 | `assets/task-10/jenkins-build-02-failed.png` | Build #2 `1.0.0-554cad3` in Jenkins (checked 2026-10-20): result FAILURE. | 2026-10-20 | verified (browser screenshot) |
| 10 | `assets/task-10/build-02-defect-console.png` | Console excerpt of build #2 (rendered from the saved log `docs/evidence/jenkins/build-02-defect-fails.log`). | 2026-10-20 | verified (rendered from real command/log output) |
| 10 | `assets/task-10/defect-branch-history.png` | The experiment branch history, the one-character diff, and the branches that contain the defect (rendered from real output, 2026-10-20). | 2026-10-20 | verified (rendered from real command/log output) |
| 10 | `assets/task-10/jenkins-build-02-failed-test.png` | Build #2's Tests page: 1 failed (`test_overlap_rules[...-True]`, marked Regression). Also notice `tests.e2e 5` - the stale report described above. | 2026-10-20 | verified (browser screenshot) |
| 10 | `assets/task-10/jenkins-build-09-tests-no-stale-report.png` | Build #9 after the report fix: 82 tests, 1 failed, and no `tests.e2e` entry. | 2026-10-20 | verified (browser screenshot) |
| 10 | `assets/task-10/jenkins-build-03-fixed.png` | Build #3 `1.0.0-30c6a05`: SUCCESS after the corrective commit. | 2026-10-20 | verified (browser screenshot) |
| 10 | `assets/task-10/build-03-fix-console.png` | Build #3 console excerpt (rendered from the saved log): tests passed, deployed, health check OK. | 2026-10-20 | verified (rendered from real command/log output) |
| 10 | `assets/task-10/build-09-rerun-console.png` | Build #9 console excerpt: `+ rm -rf reports dist`, the same failing test, later stages skipped. | 2026-10-20 | verified (rendered from real command/log output) |
| 11 | `assets/task-11/lifecycle-part1-build-run.png` | Lifecycle demo, part 1: build, tag, image labels/user/port, volume, run, `docker ps` with port mapping, `/health`, registration, logs (rendered from the real run on 2026-10-20). | 2026-10-20 | verified (rendered from real command/log output) |
| 11 | `assets/task-11/lifecycle-part2-stop-restart-volume.png` | Part 2: inspect, `whoami` = appuser, stop -> Exited, start, restart, remove, a new container on the same volume, the old account still logs in, clean-up. | 2026-10-20 | verified (rendered from real command/log output) |
| 11 | `assets/task-11/github-file-Dockerfile.png` | `Dockerfile` on GitHub. | 2026-10-20 | verified (browser screenshot) |
| 11 | `assets/task-11/github-file-docker-compose.yml.png` | `docker-compose.yml`: app + nginx, named volume, `service_healthy` dependency, `SECRET_KEY` required. | 2026-10-20 | verified (browser screenshot) |
| 11 | `assets/task-11/docker-images-containers.png` | `docker image ls`, `docker ps` and `docker volume ls` on 2026-10-20 (rendered from real output): versioned images, the running staging/prod/Jenkins/lab containers and the data volumes. | 2026-10-20 | verified (rendered from real command/log output) |
| 12 | `assets/task-12/deployed-versions.png` | Which image each environment runs, both `/health` answers, and the registry catalogue and tags (rendered from real output, 2026-10-20). | 2026-10-20 | verified (rendered from real command/log output) |
| 12 | `assets/task-12/registry-tags.png` | http://localhost:5000/v2/hotel-booking-app/tags/list in the browser. | 2026-10-20 | verified (browser screenshot) |
| 12 | `assets/task-12/prod-health.png` | http://localhost:8082/health: prod runs release 1.1.0 (`d07929b`). | 2026-10-20 | verified (browser screenshot) |
| 12 | `assets/task-12/jenkins-build-11-deployment-record.png` | `reports/deployment.txt` archived by build #11: environment, branch, version, commit, image names, URL. | 2026-10-20 | verified (browser screenshot) |
| 12 | `assets/task-12/prod-portal-v1.1.0.png` | The prod portal at http://localhost:8082 - the deployed v1.1.0 interface (the newer UI redesign is not deployed yet). | 2026-10-20 | verified (browser screenshot) |
| 13 | `assets/task-13/ansible-run1-first-deploy-v1.0.0.png` | Run 1 on a fresh lab server, from a clean clone of tag v1.0.0 (rendered from the real run on 2026-10-20). | 2026-10-20 | verified (rendered from real command/log output) |
| 13 | `assets/task-13/github-file-deploy_ansible_inventory.ini.png` | `deploy/ansible/inventory.ini` on GitHub - group `[web]`. | 2026-10-20 | verified (browser screenshot) |
| 13 | `assets/task-13/github-file-deploy_ansible_group_vars_web.yml.png` | `group_vars/web.yml`: environment-specific values, the version taken from `VERSION`, and the generated secret key. | 2026-10-20 | verified (browser screenshot) |
| 13 | `assets/task-13/github-file-deploy_ansible_playbook.yml.png` | `playbook.yml` on GitHub: the tasks listed above. | 2026-10-20 | verified (browser screenshot) |
| 13 | `assets/task-13/lab-server-state.png` | Inside the lab server (rendered from real output, 2026-10-20): file permissions (`600 root .env`), the files in `/opt/hotel-booking`, images, running containers, `docker` enabled. | 2026-10-20 | verified (rendered from real command/log output) |
| 14 | `assets/task-14/ansible-run2-upgrade-v1.1.0.png` | Run 2 (upgrade to v1.1.0): `changed=5`, `/health` 1.1.0 (rendered from the real run, 2026-10-20). | 2026-10-20 | verified (rendered from real command/log output) |
| 14 | `assets/task-14/ansible-run3-repeat-idempotent.png` | Run 3, the same playbook again: every task `ok` or `skipping`, `PLAY RECAP ... changed=0`. | 2026-10-20 | verified (rendered from real command/log output) |
| 14 | `assets/task-14/ansible-run4-rollback.png` | `rollback.yml`: "Rolled back from 1.1.0 to 1.0.0", `changed=3`, `/health` 1.0.0. | 2026-10-20 | verified (rendered from real command/log output) |
| 14 | `assets/task-14/ansible-run5-e2e-after-rollback.png` | The five v1.0.0 Selenium journeys pass against the rolled-back server. | 2026-10-20 | verified (rendered from real command/log output) |
| 14 | `assets/task-14/lab-server-health-after-rollback.png` | http://localhost:8088/health: version 1.0.0, commit `224de14`. | 2026-10-20 | verified (browser screenshot) |
| 14 | `assets/task-14/lab-server-after-rollback-v1.0.0.png` | The portal served by the lab server after the rollback (v1.0.0 interface). | 2026-10-20 | verified (browser screenshot) |
| 14 | `assets/task-14/github-file-deploy_ansible_rollback.yml.png` | `deploy/ansible/rollback.yml` on GitHub. | 2026-10-20 | verified (browser screenshot) |
| 15 | `assets/task-15/all-environments-health.png` | `/health` of development, staging, prod and the lab server (rendered from real output, 2026-10-20). | 2026-10-20 | verified (rendered from real command/log output) |
| 15 | `assets/task-15/git-status-final.png` | Current branch and uncommitted files (rendered from real output): the UI redesign and these reports are not yet committed. | 2026-10-20 | verified (rendered from real command/log output) |
| 15 | `assets/task-15/app-desktop-06-availability-logged-in.png` | The customer journey's central page: availability with totals for the stay (redesigned UI, working tree). | 2026-10-20 | verified (browser screenshot) |
| 15 | `assets/task-15/github-doc-15-task-checklist.png` | `docs/15-task-checklist.md` on GitHub: gap analysis and the final deliverable status. | 2026-10-20 | verified (browser screenshot) |
| 15 | `assets/task-15/github-doc-08-project-report.png` | `docs/08-project-report.md` on GitHub: summary, document map, end-to-end sequence diagram, setup guide, troubleshooting, limitations, future work and the demo checklist. | 2026-10-20 | verified (browser screenshot) |

## Awaiting manual capture (external actions)

| Task | File | Purpose | Status |
|---|---|---|---|
| 2 | `assets/task-02/github-issues-created.png` | Issues HB-01..HB-15 on GitHub | awaiting manual capture |
| 4 | `assets/task-04/github-branch-protection.png` | Branch protection settings (only if configured) | awaiting manual capture |
| 5 | `assets/task-05/github-pr-open.png` | A real pull request | awaiting manual capture |
| 5 | `assets/task-05/github-pr-review-comment.png` | A review comment | awaiting manual capture |
| 5 | `assets/task-05/github-pr-merged.png` | The merged pull request | awaiting manual capture |
| 9 | `(video/photo)` | Visible browser run with HEADLESS=0 (live demo) | awaiting manual capture |
| 12 | `assets/task-12/dockerhub-repository.png` | Image published on Docker Hub | awaiting manual capture |
| 13 | `assets/task-13/real-vm-run.png` | Playbook against a real Ubuntu VM | awaiting manual capture |
| 15 | `(video)` | Demo recording | awaiting manual capture |
