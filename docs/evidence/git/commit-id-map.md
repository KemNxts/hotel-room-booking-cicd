# Commit ID map (history rewrite, 2026-10-12)

On 2026-10-12, before publishing to GitHub, the commit messages in this
repository were edited to remove a co-author trailer line. Nothing else
changed: every commit keeps its author, date, the rest of its message and its file
contents (the file trees are byte-for-byte identical), but because a
commit ID is a hash that includes the message, every ID changed.

Evidence in `docs/` (Jenkins console logs, Git logs, reports) was captured
from real runs **before** the rewrite, so it cites the **original** IDs.
Those files were deliberately left untouched. Use this table to find the
current commit for any ID quoted in the evidence.

Rows marked **yes** are IDs that appear somewhere in `docs/`.

| Original ID | Current ID | Cited in docs | Subject |
|---|---|---|---|
| `c8ced9f` | `f32f905` |  | Merge branch 'docs/final-build-record' into develop |
| `636e4c0` | `5fe1e7b` |  | docs: record final green pipeline run (build #10) |
| `27aaca0` | `364c506` |  | docs: bring project documentation and pipeline fix to main |
| `2e4c93a` | `09d322f` | yes | Merge branch 'feature/project-docs' into develop |
| `58523f1` | `a3317da` |  | docs: add project report, SRS, agile plan and 15-task checklist |
| `c72fb26` | `c9042e6` |  | docs: add genuine evidence from pipeline, Docker, Git and Ansible runs |
| `60c2b5c` | `4bd3d05` |  | test: add script to capture screenshots of the running system |
| `8505486` | `a3d8626` | yes | fix: stop Jenkins publishing stale test reports from earlier builds |
| `9479383` | `32d5f8e` |  | fix: stop Jenkins publishing stale test reports from earlier builds |
| `848d710` | `10849e2` | yes | Merge branch 'fix/jenkins-stale-reports' into develop |
| `d07929b` | `ce1726d` | yes | release: v1.1.0 |
| `6f80034` | `2d67e39` |  | feat: show number of nights in the My bookings list |
| `5aa909d` | `009b38d` |  | chore: bump version to 1.1.0 |
| `9969df6` | `78d9860` | yes | Merge branch 'feature/nights-column' into develop |
| `661751d` | `224de14` | yes | release: v1.0.0 |
| `224384f` | `a2bb052` | yes | Merge branch 'feature/ansible-rollback' into develop |
| `4396fc8` | `2996699` |  | feat: versioned Ansible deploys with rollback playbook and test lab |
| `8728b62` | `9e766ac` | yes | Merge branch 'feature/release-footer' into develop |
| `cfeacef` | `4463add` | yes | Merge branch 'feature/contact-footer' into develop |
| `65ad990` | `74a153d` | yes | feat: add hotel contact details footer to every page |
| `c24148f` | `63498a8` | yes | feat: show running release and environment in page footer |
| `30c6a05` | `2fb62d6` | yes | fix: restore strict overlap comparison in booking DAO |
| `554cad3` | `5844eec` | yes | experiment: introduce deliberate off-by-one defect in overlap rule |
| `f4d0b26` | `da225fb` | yes | Merge branch 'feature/ci-release-pipeline' into develop |
| `64351fe` | `6fd87b5` | yes | ci: add lint, versioned images, registry publish and verified deploy |
| `37a4663` | `bdfc2fb` | yes | Merge branch 'feature/security-hardening' into develop |
| `388c47b` | `fd3cb60` | yes | test: add route-level integration tests and database rule tests |
| `65c41cb` | `716b910` | yes | feat: add CSRF protection, secure cookies, audit logs and DB overlap guard |
| `863f4f5` | `4b1cd61` |  | docs: document Jenkins and Ansible usage and add viva notes |
| `d670fad` | `475cecd` | yes | Merge branch 'feature/ansible' into develop |
| `796232a` | `ca48776` |  | feat: add Ansible inventory and playbook to provision and deploy |
| `9c6fcf4` | `6d808a3` | yes | Merge branch 'feature/jenkins-pipeline' into develop |
| `f9cd7b4` | `7c5203c` |  | ci: add ready-to-run local Jenkins image and compose file |
| `160c5a5` | `9e3bc20` |  | ci: add Jenkins pipeline with test gates and parameterised deploy |
| `0602c39` | `984a568` | yes | Merge branch 'feature/docker' into develop |
| `424f194` | `e5c3c5d` |  | docs: add container lifecycle guide and Docker run instructions |
| `28c161d` | `0555f12` |  | build: containerise app with Gunicorn and Nginx reverse proxy |
| `72b99f1` | `cff7b66` |  | feat: require SECRET_KEY outside dev/test; let e2e use system Chromium |
| `1ebec7c` | `e819cea` | yes | Merge branch 'feature/tests' into develop |
| `db3f42d` | `5fc57e8` |  | docs: explain how to run unit and e2e tests |
| `e997711` | `555f30e` |  | test: add Selenium journeys with screenshot on failure |
| `18eab9d` | `4c1d1c0` |  | test: add pytest unit tests for auth and booking services |
| `1677565` | `c18cfc5` | yes | Merge branch 'feature/app-mvp' into develop |
| `b7c8733` | `2bea3f4` |  | docs: document architecture, local setup and configuration |
| `03175ab` | `ac05514` |  | feat: add Flask controllers and templates for all MVP features |
| `1fd1bec` | `094eac0` |  | feat: add auth and booking services with business rules |
| `29633dc` | `fc83f50` |  | build: add Flask/Gunicorn deps, config, SQLite schema, models and DAO layer |
| `08702db` | `541dad5` | yes | chore: initialise repository skeleton |
