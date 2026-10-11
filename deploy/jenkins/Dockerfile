# A local Jenkins for this project: official Jenkins LTS + every tool the
# Jenkinsfile needs. Started by deploy/jenkins/docker-compose.yml.
FROM jenkins/jenkins:lts-jdk21

USER root

# Optional extra root certificates from the repo's certs/ folder (normally
# none; see certs/README.md). Added to the system store (git, pip via
# PIP_CERT, docker builds via the Jenkinsfile) and to Java's store
# (plugin downloads).
COPY --from=certs . /usr/local/share/ca-certificates/extra/
RUN update-ca-certificates >/dev/null \
    && for c in /usr/local/share/ca-certificates/extra/*.crt; do \
         [ -e "$c" ] && keytool -importcert -noprompt -cacerts -storepass changeit \
              -alias "extra-$(basename "$c")" -file "$c"; \
       done; true
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt

# Python 3.11 (same version as the production image), copied from the
# official Python image built on the same Debian release as Jenkins.
COPY --from=python:3.11-slim-trixie /usr/local/bin/python3.11 /usr/local/bin/python3.11
COPY --from=python:3.11-slim-trixie /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=python:3.11-slim-trixie /usr/local/lib/libpython3.11.so.1.0 /usr/local/lib/

# Docker CLI + compose/buildx plugins. Jenkins does not run its own Docker
# daemon: it talks to the host's daemon through the mounted docker.sock.
COPY --from=docker:29-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:29-cli /usr/local/libexec/docker/cli-plugins /usr/local/libexec/docker/cli-plugins

# Chromium + chromedriver for the Selenium tests, and the shared libraries
# Python 3.11 needs. `git config ... safe.directory` lets git read the
# repository mounted from the host (owned by a different user).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        chromium chromium-driver \
        libssl3t64 libsqlite3-0 libffi8 libbz2-1.0 liblzma5 zlib1g libexpat1 \
        libuuid1 libncursesw6 libreadline8t64 \
    && rm -rf /var/lib/apt/lists/* \
    && ldconfig \
    && git config --system --add safe.directory '*'

# Tell the e2e tests where the browser and driver are (see tests/e2e/conftest.py).
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER=/usr/bin/chromedriver

USER jenkins

# Pre-install plugins, and a start-up script that creates the admin user,
# the SECRET_KEY credential and the pipeline job.
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt
COPY init.groovy.d/ /usr/share/jenkins/ref/init.groovy.d/
