# Task 8 - viva questions and answers

**Task 8 - Pipeline as Code and Server Deployment**

Source: section G of [task-08-pipeline-as-code-and-deployment.md](../../task-08-pipeline-as-code-and-deployment.md) - answers checked against the
repository and the evidence in this project.

1. **What is "pipeline as code"?** The pipeline is a file (`Jenkinsfile`) in
   the repository, so it is versioned, reviewed and identical on every run.
2. **Name your stages in order.** Checkout, Install dependencies, Static
   checks, Unit & integration tests, E2E tests, Package source, Build images,
   Publish images, Deploy, Health check.
3. **Which setting is parameterised?** `APP_ENV`: staging or prod - it changes
   the app environment, the port (8081/8082) and the compose project (separate data).
4. **How are secrets handled?** `SECRET_KEY` is a Jenkins credential injected
   with `withCredentials` only in Deploy/Health check and masked in logs; nothing secret is in Git.
5. **What happens if a test fails?** That stage fails and every later stage,
   including Deploy, is skipped (build #2 shows this).
6. **(Project-specific) How do you know the deployed version is the tested one?**
   Images are tagged `<version>-<commit>`; the health-check stage compares the
   version and commit returned by `/health` with the ones built.
7. **(Project-specific) Where does it deploy?** To a Docker Compose stack on
   the Jenkins host: staging :8081, prod :8082. Real servers are handled by Ansible.
8. **Why `--wait` on `docker compose up`?** It waits until containers are
   healthy (Docker HEALTHCHECK) and fails the stage if they never are.
9. **What is `post { always }` for?** It publishes test reports and archives
   artifacts even when the build fails, so failures can be analysed.
10. **Why `disableConcurrentBuilds`?** Two deployments at the same time would fight over the same containers.
11. **What is `deployment.txt`?** A record archived with each build: environment, branch, version, commit, image names, URL.

## Extra questions that match this demonstration

1. **Why is the pipeline written as a Jenkinsfile in the repository?**
   'Pipeline as code': the build and deploy process is versioned, reviewed and rolled back like the application code. Jenkins reads it from the checked-out commit, so every commit is built with the pipeline that belongs to it.

2. **Does your pipeline run a Maven build?**
   No. This is a Python project, so the build stage is dependency installation plus compileall and flake8, and the tests run with pytest. The document 03-srs-architecture.md explains the Java-to-Python mapping and notes that Maven would need the professor's confirmation if it is mandatory.

3. **Why does the deploy stage come after the tests?**
   Because of the quality gate: if any test or lint step fails, Jenkins skips every later stage, so only tested code is packaged, published and deployed. The deploy stage also waits for the containers to be healthy and the health stage checks that the running version and commit are the ones just built.

4. **Which environment did this build deploy to, and how is that chosen?**
   Staging, on port 8081. The APP_ENV parameter chooses it: staging uses port 8081 and the Docker Compose project hotel-staging, prod uses 8082 and hotel-prod, with separate containers and data volumes.
