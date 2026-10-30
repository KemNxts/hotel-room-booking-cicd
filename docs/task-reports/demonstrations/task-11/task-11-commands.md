# Task 11 - command sheet

**Task 11 - Docker Image and Container Lifecycle**

## Before you start

- Docker Desktop must be running (it does not start automatically after a reboot): `docker info` must answer.
- Port 18000 on your computer must be free. The demo uses its own container names (`hotel-demo-app`, `hotel-demo-app2`), image tags (`hotel-booking-app:demo`, `:demo-copy`) and volume (`hotel-demo-data`) and deletes them at the end. The project's real staging, prod, Jenkins and registry containers are not touched.
- If your network scans HTTPS (Avast), the `certs/` folder is copied into the image so `pip` works inside the build (see certs/README.md). The first build can take a few minutes; later builds use the cache.
- Open PowerShell in the project folder.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | The Dockerfile: building the image (1/2) | `Get-Content Dockerfile \| Select-String -NotMatch '^\s*(#\|$)' \| Select-Object -First 17` | FROM python:3.11-slim, ARG APP_VERSION and GIT_COMMIT, ENV settings (DATABASE_PATH=/data/hotel.db), LABELs, WORKDIR, copying certs and requirements, pip install. |
| 2 | The Dockerfile (2/2): safe defaults | `Get-Content Dockerfile \| Select-String -NotMatch '^\s*(#\|$)' \| Select-Object -Skip 17` | COPY app, useradd appuser, USER appuser, VOLUME /data, EXPOSE 8000, HEALTHCHECK calling /health, CMD gunicorn. |
| 3 | Docker Compose: the whole stack | `Get-Content docker-compose.yml \| Select-String -NotMatch '^\s*#' \| Select-String -Pattern '^services\|^  app:\|^  nginx:\|image:\|ports:\|HOST_PORT\|volumes:\|hotel-data\|restart:\|condition\|SECRET_KEY' \| ForEach-Object { $_.Line }` | Two services app and nginx, image names with IMAGE_TAG, the SECRET_KEY requirement, the hotel-data volume, the published port, depends_on healthy and restart: unless-stopped. |
| 4 | Image versus container | `docker images hotel-booking-app --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}'; docker ps -a --filter name=hotel- --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'` | First the image templates (tags 1.1.0 and latest); then the containers of the project (staging, prod, Jenkins, registry, Ansible lab) with their images and status. |
| 5 | Build and tag an image | `docker build -q -t hotel-booking-app:demo --build-arg APP_VERSION=1.1.0-demo --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) .; docker tag hotel-booking-app:demo hotel-booking-app:demo-copy; docker images hotel-booking-app --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}'` | The build prints the new image id (sha256:...). The listing then shows tags demo and demo-copy with the same IMAGE ID, next to 1.1.0 and latest. |
| 6 | Run a container with a port and a volume | `docker run -d --name hotel-demo-app -p 18000:8000 -e SECRET_KEY=demo-only-not-a-real-secret -v hotel-demo-data:/data hotel-booking-app:demo \| Out-Null; Start-Sleep 14; docker ps --filter name=hotel-demo-app --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'; curl.exe -s http://localhost:18000/health` | Status 'Up ... (healthy)', the port mapping 0.0.0.0:18000->8000/tcp, and JSON with status ok, version 1.1.0-demo and the commit id. |
| 7 | Inspect the container | `docker inspect hotel-demo-app --format 'state={{.State.Status}} health={{.State.Health.Status}} restart-policy={{.HostConfig.RestartPolicy.Name}} image={{.Config.Image}}'; docker inspect hotel-demo-app --format 'ports: {{json .NetworkSettings.Ports}}'; docker inspect hotel-demo-app --format '{{range .Mounts}}volume {{.Name}} -> {{.Destination}}{{end}}'` | state=running health=healthy restart-policy=no image=hotel-booking-app:demo; the port 8000/tcp mapped to host port 18000; volume hotel-demo-data -> /data. |
| 8 | Logs | `docker logs --tail 10 hotel-demo-app` | Gunicorn start-up lines and request log lines for /health. |
| 9 | Stop, start and restart | `docker stop hotel-demo-app \| Out-Null; docker ps -a --filter name=hotel-demo-app --format '{{.Names}}: {{.Status}}'; docker start hotel-demo-app \| Out-Null; Start-Sleep 14; docker ps --filter name=hotel-demo-app --format '{{.Names}}: {{.Status}}'; docker restart hotel-demo-app \| Out-Null; 'restarted with docker restart'` | First 'Exited (0)...', then 'Up ... (healthy)' after start, then the restart confirmation. |
| 10 | Persistent storage: writing data | `docker exec hotel-demo-app python -c "import sqlite3; c = sqlite3.connect('/data/hotel.db'); c.execute('INSERT INTO users (email, full_name, password_hash) VALUES (?, ?, ?)', ('persist@example.com', 'Persist Test', 'x')); c.commit(); print('users in database:', c.execute('SELECT COUNT(*) FROM users').fetchone()[0])"` | users in database: 1 |
| 11 | Persistent storage: remove the container, keep the data | `docker rm -f hotel-demo-app \| Out-Null; docker run -d --name hotel-demo-app2 -p 18000:8000 -e SECRET_KEY=demo-only-not-a-real-secret -v hotel-demo-data:/data hotel-booking-app:demo \| Out-Null; Start-Sleep 12; docker exec hotel-demo-app2 python -c "import sqlite3; print('users after the old container was deleted:', sqlite3.connect('/data/hotel.db').execute('SELECT COUNT(*) FROM users').fetchone()[0])"` | users after the old container was deleted: 1 - the data survived because it is stored in the volume. |
| 12 | Clean up the demo objects | `docker rm -f hotel-demo-app2 \| Out-Null; docker volume rm hotel-demo-data \| Out-Null; docker rmi hotel-booking-app:demo hotel-booking-app:demo-copy \| Out-Null; 'demo containers left: ' + (docker ps -a --filter name=hotel-demo --format '{{.Names}}' \| Measure-Object).Count; docker volume ls --format '{{.Name}}' \| Select-String 'hotel'` | 'demo containers left: 0' and the project's own volumes (hotel-prod_hotel-data, hotel-staging_hotel-data, hotel-jenkins_..., hotel-ansible-lab_...). |

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- Start the full stack (app + nginx) with Compose, as Jenkins does:

  ```powershell
  $env:SECRET_KEY='any-long-random-text'; $env:HOST_PORT='8090'; docker compose -p hotel-try up -d --build --wait
  ```

- Throw that stack away again (the -v also deletes its database volume):

  ```powershell
  docker compose -p hotel-try down -v
  ```

- Read the project's own lifecycle notes:

  ```powershell
  Get-Content docs/container-lifecycle.md
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| 'failed to connect to the docker API' / pipe not found | Docker Desktop is not running. Start it from the Start menu, wait until it says 'Engine running' (about a minute), then repeat. |
| 'port is already allocated' | `docker ps` shows who uses 18000. Remove an old demo container: `docker rm -f hotel-demo-app hotel-demo-app2`. |
| 'container name already in use' | `docker rm -f hotel-demo-app hotel-demo-app2`, then run the step again. |
| The build fails with CERTIFICATE_VERIFY_FAILED | Antivirus HTTPS scanning. Put the antivirus root certificate in certs/ as a .crt file (see certs/README.md) and build again. |
| /health does not answer right after `docker run` | Wait 10-15 seconds (the health check start period), then `curl.exe -s http://localhost:18000/health`. See `docker logs hotel-demo-app` for errors. |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 11
```
