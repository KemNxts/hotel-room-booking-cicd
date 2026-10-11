# 7. Configuration Management with Ansible (Tasks 13, 14)

## Files

| File | Purpose |
|---|---|
| `deploy/ansible/inventory.ini` | Real servers (group `[web]`): edit `ansible_host` / `ansible_user` |
| `deploy/ansible/group_vars/web.yml` | Variables: `app_dir`, `app_env`, `host_port`, `app_version` (from `VERSION`), `git_commit`, `secret_key` |
| `deploy/ansible/ansible.cfg` | Inventory path, interpreter, lab host-key setting |
| `deploy/ansible/playbook.yml` | Provision + deploy |
| `deploy/ansible/rollback.yml` | Return to the previous (or a named) release |
| `deploy/ansible/Dockerfile` | Ansible controller image (Ansible does not run natively on Windows) |
| `deploy/ansible/lab/` | Disposable Ubuntu 24.04 "server" container + inventory, for practice without a VM |

## What the playbook automates (Task 13)

| Prerequisite | Task(s) |
|---|---|
| Required packages | `apt`: `docker.io`, `docker-compose-v2` |
| Service setup | `service`: docker started + enabled on boot; containers use `restart: unless-stopped` |
| Deployment directories | `file`: `/opt/hotel-booking`, `.../deploy` (root, 0755) |
| Application files | `copy`: app source, Dockerfile, compose file, Nginx config, VERSION, certs |
| Application configuration | `copy`: `.env` with SECRET_KEY, APP_ENV, HOST_PORT, version, IMAGE_TAG - **mode 0600**, `no_log` |
| Nginx configuration | baked into the `hotel-booking-nginx` image (`deploy/nginx/hotel.conf`) |
| Network port | `host_port` variable (80) published by the Nginx container |
| Build / start | images built only if this release+commit is not built yet; `docker compose up -d --wait` |
| Health verification | `uri` GET `/health` with retries + `assert` the running version is the expected one |

**Environment-specific values are variables** (`group_vars/web.yml`, or
`-e app_env=staging -e host_port=8080` on the command line).

**Safety:** only built-in modules; nothing outside `/opt/hotel-booking`
besides installing Docker. The playbook does **not** change SSH settings or
firewall rules; if `ufw` is active on your server, allow `host_port`
yourself after checking what else is exposed. The `SECRET_KEY` is generated
once on the control machine (`deploy/ansible/credentials/secret_key`,
git-ignored) and never printed.

## Idempotency

Each task describes a **desired state** ("Docker is installed", "this file
has this content"), so Ansible only acts when reality differs. One special
case: rebuilding a Docker image always produces a new image ID, which would
make compose restart containers on every run. The playbook therefore builds
only when no image exists for this release **and** commit (checked through the
image label `org.opencontainers.image.revision`).

## Rollback (Task 14)

Every deploy tags images with the release (`hotel-booking-app:1.1.0`) and
keeps older images. Before switching releases, the playbook writes the
currently running release to `/opt/hotel-booking/previous_release`.

`rollback.yml`:

1. reads `previous_release` (or uses `-e rollback_to=1.0.0`);
2. refuses to continue if that release's images are not on the server;
3. sets `IMAGE_TAG` in `.env`, saves the release it is leaving (so running
   it again rolls forward);
4. `docker compose up -d --no-build --wait` (no rebuild - the exact image
   that ran before);
5. checks `/health` and **asserts the version is the target version**.

Data is kept (same volume). Limits: a few seconds' downtime while the
containers are re-created; database schema changes would need a migration
plan (none so far).

## Evidence: first run, upgrade, idempotent re-run, rollback

All runs used the lab: a **fresh** Ubuntu 24.04 container (systemd + SSH, no
Docker installed), deployed from clean clones of the tags `v1.0.0` and
`v1.1.0`. Unedited output: [evidence/ansible/](evidence/ansible/).

| Run | Command | Result (PLAY RECAP) | /health afterwards |
|---|---|---|---|
| 1 First provisioning | `playbook.yml` from tag v1.0.0 | ok=14 **changed=7** failed=0 | `1.0.0`, commit `661751d` |
| 2 Upgrade | `playbook.yml` from tag v1.1.0 | ok=15 changed=5 failed=0 | `1.1.0`, commit `d07929b` |
| 3 Repeat (idempotency) | `playbook.yml` from tag v1.1.0 again | ok=13 **changed=0** failed=0 | `1.1.0` |
| 4 Rollback | `rollback.yml` | ok=11 changed=3 failed=0, "Rolled back from 1.1.0 to 1.0.0" | `1.0.0`, commit `661751d` |
| 5 Restored release works | `E2E_BASE_URL=http://localhost:8088 pytest -m e2e` | **5 passed** | - |

Screenshot of the rolled-back server (footer "Release 1.0.0 · prod"):
`evidence/screenshots/ansible-lab-after-rollback-v1.0.0.png`.

**Honest limitation:** these runs targeted a privileged Docker container
standing in for a server, not a real VM or cloud machine. The playbook uses
only standard Ubuntu packages and SSH, so it should behave the same on a
real Ubuntu 22.04/24.04 server, but that was **not** tested.

## How to run it

### Option A - the lab (no VM needed)

```powershell
cd deploy\ansible\lab
docker compose up -d --build target          # fresh "server"
docker compose run --rm controller ansible-playbook -i lab/inventory.ini playbook.yml
docker compose run --rm controller ansible-playbook -i lab/inventory.ini playbook.yml   # again: changed=0
#   -> http://localhost:8088
docker compose run --rm controller ansible-playbook -i lab/inventory.ini rollback.yml   # needs an earlier release deployed first
docker compose down -v                       # throw the lab away
```

To produce an upgrade + rollback yourself: deploy, bump `VERSION` (e.g.
1.1.0 -> 1.2.0) and commit, deploy again, then run `rollback.yml`.

### Option B - a real Ubuntu server/VM

1. Put the IP and user in `deploy/ansible/inventory.ini`.
2. From the repository root:
   ```powershell
   docker build -t hotel-ansible -f deploy/ansible/Dockerfile .
   docker run --rm -it -v "${PWD}:/work" hotel-ansible ansible-playbook playbook.yml --ask-pass --ask-become-pass
   ```
   (or on Linux/macOS with Ansible installed: `cd deploy/ansible && ansible-playbook playbook.yml`)
3. Dry run first if you like: add `--check`.
