# Evidence

Everything in this folder is **real output** captured on 2026-10-11 on the
development machine (Windows 11 + Docker Desktop). Nothing was edited
except replacing a temporary folder path with `<scratch>`. Secrets were
checked and do not appear in any file.

| Folder / file | What it shows | Task |
|---|---|---|
| `tests/local-run.txt` | flake8 clean + all 90 tests passing (verbose) | 3, 9 |
| `tests/junit-all.xml` | JUnit XML report of that run | 9 |
| `git/merge-conflict.txt` | A real 3-file merge conflict, its resolution commit and the graph | 6 |
| `jenkins/build-01-green-staging.log` | First full green pipeline run, deploy to staging | 7, 8, 12 |
| `jenkins/build-02-defect-fails.log` | Deliberate defect: unit test fails, later stages skipped | 10 |
| `jenkins/build-03-fix-green.log` | Corrective commit: green again and deployed | 10 |
| `jenkins/build-05-release-v1.0.0-prod.log` | Release v1.0.0 from `main` to prod | 12, 15 |
| `jenkins/build-09-defect-rerun-after-report-fix.log` | Defect re-run after fixing stale test reports | 10 |
| `docker/lifecycle.txt` | build, tag, run, ports, logs, inspect, stop/start/restart/rm, data persistence | 11 |
| `docker/rollback-prod.txt` | prod rolled back 1.1.0 -> 1.0.0 and forward with Compose | 14 |
| `ansible/run1-first-deploy-v1.0.0.txt` | First provisioning of a fresh server | 13, 14 |
| `ansible/run2-upgrade-v1.1.0.txt` | Upgrade to v1.1.0 | 13 |
| `ansible/run3-repeat-idempotent.txt` | Same run again: `changed=0` | 14 |
| `ansible/run4-rollback.txt` | `rollback.yml` back to 1.0.0, verified | 14 |
| `ansible/run5-e2e-after-rollback.txt` | 5/5 Selenium journeys pass on the restored release | 14 |
| `screenshots/app-*.png` | The portal: rooms, register, availability, pending/confirmed/cancelled, My bookings | 6, 9 |
| `screenshots/jenkins-*.png` | Stage view (incl. failed #2), last build, test results, failed test | 7, 10 |
| `screenshots/ansible-lab-after-rollback-v1.0.0.png` | Footer shows "Release 1.0.0" after rollback | 14 |

Jenkins build list for reference: #1-#9 (see `docs/05-ci-cd-pipeline.md`).
Logs for #4, #6, #7, #8 are in Jenkins itself (Console Output) - only the
key builds were copied here.

Re-take the screenshots any time (creates demo bookings in the target app):

```powershell
python scripts/capture_screenshots.py --app http://localhost:8082 --jenkins http://localhost:8090 --jenkins-password <admin password>
```
