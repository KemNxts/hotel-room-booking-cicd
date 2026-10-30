# Task 7 - viva questions and answers

**Task 7 - Jenkins Installation and Continuous Integration**

Source: section G of [task-07-jenkins-installation-and-ci.md](../../task-07-jenkins-installation-and-ci.md) - answers checked against the
repository and the evidence in this project.

1. **What is Jenkins?** An automation server that runs build/test/deploy jobs automatically.
2. **What is Continuous Integration?** Automatically building and testing every change soon after it is committed, so errors are found quickly.
3. **Installed Jenkins vs Jenkinsfile vs executed build?** The server, the
   pipeline definition stored in Git, and an actual numbered run with results.
   Only a build (e.g. #11) proves it works.
4. **How is your build triggered?** Poll SCM every ~5 minutes, plus manual
   *Build with Parameters*. A webhook isn't possible because GitHub cannot reach localhost.
5. **How do you install dependencies reproducibly?** A fresh venv each build
   and `pip install -r requirements-dev.txt` with pinned versions (`Flask==3.1.3`, `pytest==9.1.1`...).
6. **What does flake8 check?** Syntax errors, undefined names, unused imports and style (config in `.flake8`, line length 110).
7. **Where do the test reports come from?** pytest writes JUnit XML
   (`--junitxml`), and the JUnit plugin shows them on the Tests page.
8. **(Project-specific) What artifacts does a build keep?** The source
   archive `hotel-booking-<version>-<commit>.tar.gz` with its sha256, test XML,
   `health.json` and `deployment.txt`.
9. **(Project-specific) Why run Jenkins in Docker?** The whole server
   (plugins, Python, Chromium, Docker CLI, the job) is defined in files in
   `deploy/jenkins/` and starts with one command; nothing is clicked by hand.
10. **Is this a Maven job?** No. The project is Python; pip, flake8 and
    pytest do the jobs Maven would do for Java. I'll confirm with the professor that this is acceptable.
11. **What is an agent?** The machine that executes the steps; here the
    built-in node (the Jenkins container), which uses the host's Docker through the mounted socket.

## Extra questions that match this demonstration

1. **Jenkins is installed as a Docker container, not as a Windows program. Why?**
   A container is reproducible: one compose file and one Dockerfile give the same Jenkins (LTS, Python 3.11, Chromium, Docker CLI, plugins) on any machine, and it can be deleted and rebuilt. The Jenkins data (jobs, builds, credentials) lives in a named volume, jenkins-home, so it survives container restarts.

2. **What is the difference between a Jenkinsfile existing, a job being configured, and a job running successfully?**
   Three separate facts. The Jenkinsfile is just a file in Git. The job is Jenkins's own configuration that points to the repository and the Jenkinsfile. A successful run is a build record, with its stages, tests and artifacts. In the video each one is proven separately: git ls-files, the job's config.xml, and the build list from the API.

3. **Does this Jenkins job build a Maven project?**
   No. It checks out Git, installs Python dependencies with pip, lints with flake8, runs pytest and Selenium, and builds Docker images. The Python equivalent of a Maven build is described in docs/03-srs-architecture.md.
