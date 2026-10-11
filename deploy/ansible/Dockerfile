# Ansible does not run natively on Windows. This image is a ready-made
# Ansible "control node" so you can run the playbook from any machine with Docker.
# Build from the REPOSITORY ROOT (it needs the certs/ folder):
#
#   docker build -t hotel-ansible -f deploy/ansible/Dockerfile .
#   docker run --rm -it -v "${PWD}:/work" hotel-ansible ansible-playbook playbook.yml --ask-pass --ask-become-pass
FROM python:3.12-slim

# ssh client to reach the servers; sshpass enables password login (--ask-pass);
# git lets the playbook record which commit it deploys.
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-client sshpass git \
    && rm -rf /var/lib/apt/lists/* \
    && git config --system --add safe.directory '*'

# Optional extra root certificates (see certs/README.md).
COPY certs/ /usr/local/share/ca-certificates/extra/
RUN update-ca-certificates >/dev/null \
    && pip install --no-cache-dir --cert /etc/ssl/certs/ca-certificates.crt ansible-core==2.21.5

# The repository is mounted at /work. Point Ansible at our config file
# explicitly: Ansible ignores ansible.cfg in world-writable folders, which is
# how Windows folders appear inside Linux containers.
ENV ANSIBLE_CONFIG=/work/deploy/ansible/ansible.cfg
WORKDIR /work/deploy/ansible
