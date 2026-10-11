# Ansible does not run natively on Windows. This image is a ready-made
# Ansible "control node" so you can run the playbook from any machine with Docker.
#
#   docker build -t hotel-ansible deploy/ansible
#   docker run --rm -it -v "${PWD}:/work" hotel-ansible ansible-playbook playbook.yml --ask-pass --ask-become-pass
FROM python:3.12-slim

# ssh client to reach the servers; sshpass enables password login (--ask-pass).
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-client sshpass \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir ansible-core==2.21.5

# The repository is mounted at /work. Point Ansible at our config file
# explicitly: Ansible ignores ansible.cfg in world-writable folders, which is
# how Windows folders appear inside Linux containers.
ENV ANSIBLE_CONFIG=/work/deploy/ansible/ansible.cfg
WORKDIR /work/deploy/ansible
