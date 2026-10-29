# Task Reports - CI/CD Pipeline for a Hotel Room Booking Portal

One self-contained report per professor-assigned task. Each report has the
same structure: **A** objective and status, **B** beginner explanation,
**C** what was implemented, **D** screenshots and evidence, **E** how to
demonstrate it, **F** screenshot checklist, **G** viva questions and answers,
**H** troubleshooting, **I** revision notes.

Start with the audit: [00-project-audit.md](00-project-audit.md) - the real
state of the repository, services and evidence on 2026-10-20.

| # | Report | In one sentence | Status |
|---|---|---|---|
| 1 | [Problem Definition and Scope](task-01-problem-definition-and-scope.md) | why a booking portal and a delivery pipeline are needed, and how success is measured | Implemented and verified |
| 2 | [Agile Planning and DevOps Workflow](task-02-agile-planning-and-devops-workflow.md) | user stories, backlog, board, sprints, Definition of Done and the lifecycle diagram | **Partially completed** - GitHub issues pending |
| 3 | [Requirements, Architecture and Setup](task-03-requirements-architecture-and-setup.md) | SRS, layered Flask architecture, database, routes and local setup | Implemented and verified |
| 4 | [Git and GitHub Initialization](task-04-git-and-github-initialization.md) | repository skeleton, ignore rules, templates, branch policy, GitHub remote | Implemented and verified |
| 5 | [Feature Development and Branching](task-05-feature-development-and-branching.md) | feature branches with commits and tests merged into develop | **Partially completed** - real GitHub PRs pending |
| 6 | [MVP Completion and Collaboration](task-06-mvp-completion-and-collaboration.md) | six workflows, a real merge conflict and release tags | Implemented and verified |
| 7 | [Jenkins Installation and CI](task-07-jenkins-installation-and-ci.md) | Jenkins in Docker, the CI job, reports and artifacts | Implemented and verified (polling; Python not Maven) |
| 8 | [Pipeline as Code and Deployment](task-08-pipeline-as-code-and-deployment.md) | the 10-stage Jenkinsfile, parameter, secrets and health-checked deploy | Implemented and verified |
| 9 | [Selenium Test Design and Execution](task-09-selenium-test-design-and-execution.md) | five browser journeys, waits, isolated data, screenshots on failure | Implemented and verified |
| 10 | [Continuous Testing in Jenkins](task-10-continuous-testing-in-jenkins.md) | tests as a quality gate, proven with a deliberate defect | Implemented and verified |
| 11 | [Docker Image and Container Lifecycle](task-11-docker-image-and-container-lifecycle.md) | the Dockerfile and every lifecycle operation, incl. persistent data | Implemented and verified |
| 12 | [Jenkins-Docker Continuous Deployment](task-12-jenkins-docker-continuous-deployment.md) | version+SHA images, registry, deploy, health check, record | Implemented and verified (local registry) - Docker Hub pending |
| 13 | [Configuration Management with Ansible](task-13-configuration-management-with-ansible.md) | inventory, variables and playbook provisioning a fresh server | Implemented and verified (container lab, not a VM) |
| 14 | [Provisioning, Idempotency and Rollback](task-14-provisioning-idempotency-and-rollback.md) | `changed=0` on repeat runs and a verified rollback | Implemented and verified (container lab) |
| 15 | [End-to-End Release and Documentation](task-15-end-to-end-release-and-final-documentation.md) | the whole flow, final documentation and the 12-minute demo | Implemented and verified, with pending external items |

## Also in this folder

| File | Purpose |
|---|---|
| [VIVA_CHEAT_SHEET.md](VIVA_CHEAT_SHEET.md) | 30-second intro, 2-minute explanation, the four stories, honest answers about limitations, demo commands |
| [screenshot-index.md](screenshot-index.md) | every screenshot with task, purpose, date and status |
| [GENERATION_STATUS.md](GENERATION_STATUS.md) | progress record of this documentation pass |
| `assets/task-01/` ... `assets/task-15/` | screenshots per task (`.txt` next to rendered terminal images = the raw output) |
| `assets/raw/` | raw logs captured on 2026-10-20 (Jenkins build #11, Docker lifecycle, Ansible runs) |
| `Complete_DevOps_Project_Report.docx` / `.pdf` | all 15 reports in one document |
| `word/Task_01_...docx` ... `word/Task_15_...docx` | one Word document per task |

The Markdown files are the source of truth; the Word/PDF files are generated from them. To rebuild them after editing, see [tools/README.md](tools/README.md).

## Other project documentation

[README](../../README.md) - [Project report](../08-project-report.md) - [15-task checklist](../15-task-checklist.md) - [Viva notes](../viva-notes.md) - [Evidence](../evidence/README.md) - [UI design](../09-ui-design.md)
