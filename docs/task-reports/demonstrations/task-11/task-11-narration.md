# Task 11 - narration script

**Task 11 - Docker Image and Container Lifecycle**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

## Step 1 - The Dockerfile: building the image (1/2) [video 00:01]

**What I am doing:** running

```powershell
Get-Content Dockerfile | Select-String -NotMatch '^\s*(#|$)' | Select-Object -First 17
```

**Spoken script (as in the video):**

> This is Task 11, Docker. A Dockerfile is the recipe for an image. An image is a read only template that contains our application, Python and all dependencies. This is the first half. It starts from a small official Python image, receives the version and commit as build arguments, and stores them in environment variables and labels. Then it installs the dependencies from requirements dot txt in their own layer, so Docker can cache that step.

**What the output means:** FROM python:3.11-slim, ARG APP_VERSION and GIT_COMMIT, ENV settings (DATABASE_PATH=/data/hotel.db), LABELs, WORKDIR, copying certs and requirements, pip install.

**What I will tell the professor:** "The Dockerfile is the recipe: base image, version information, then dependencies in a cached layer."

## Step 2 - The Dockerfile (2/2): safe defaults [video 00:36]

**What I am doing:** running

```powershell
Get-Content Dockerfile | Select-String -NotMatch '^\s*(#|$)' | Select-Object -Skip 17
```

**Spoken script (as in the video):**

> The second half copies the application code, then creates a normal user, so the app does not run as root. It declares the data folder as a volume, exposes port eight thousand, and defines a health check: every ten seconds Docker calls the health address, and marks the container unhealthy after three failures. The last line starts Gunicorn, the production web server.

**What the output means:** COPY app, useradd appuser, USER appuser, VOLUME /data, EXPOSE 8000, HEALTHCHECK calling /health, CMD gunicorn.

**What I will tell the professor:** "The container runs as a non-root user with a health check and a data volume."

## Step 3 - Docker Compose: the whole stack [video 01:05]

**What I am doing:** running

```powershell
Get-Content docker-compose.yml | Select-String -NotMatch '^\s*#' | Select-String -Pattern '^services|^  app:|^  nginx:|image:|ports:|HOST_PORT|volumes:|hotel-data|restart:|condition|SECRET_KEY' | ForEach-Object { $_.Line }
```

**Spoken script (as in the video):**

> Docker Compose describes the complete application in one file. I print the important lines. The app service uses the image tagged with the version and commit, gets its settings from environment variables, and mounts the named volume hotel data. The nginx service publishes the public port, waits until the app is healthy, and both restart automatically unless stopped on purpose.

**What the output means:** Two services app and nginx, image names with IMAGE_TAG, the SECRET_KEY requirement, the hotel-data volume, the published port, depends_on healthy and restart: unless-stopped.

**What I will tell the professor:** "One Compose file defines the app, the proxy, the volume, ports and restart behaviour."

## Step 4 - Image versus container [video 01:34]

**What I am doing:** running

```powershell
docker images hotel-booking-app --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}'; docker ps -a --filter name=hotel- --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

**Spoken script (as in the video):**

> The difference between an image and a container. The images list shows templates that exist on this computer: repository, tag, image id and size. A container is a running or stopped instance of an image. It has a name, a status and its own writable layer. Like a class and an object: one image can create many containers. These are the project's existing containers, currently in whatever state they were left.

**What the output means:** First the image templates (tags 1.1.0 and latest); then the containers of the project (staging, prod, Jenkins, registry, Ansible lab) with their images and status.

**What I will tell the professor:** "An image is a template; a container is an instance of it that can run, stop and be deleted."

## Step 5 - Build and tag an image [video 02:07]

**What I am doing:** running

```powershell
docker build -q -t hotel-booking-app:demo --build-arg APP_VERSION=1.1.0-demo --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) .; docker tag hotel-booking-app:demo hotel-booking-app:demo-copy; docker images hotel-booking-app --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}'
```

**Spoken script (as in the video):**

> Now I build an image myself. Docker build reads the Dockerfile. The dash t option gives it a name and a tag, here hotel booking app, colon demo. The build arguments bake in a demo version and the real commit id. Then docker tag adds a second name to the same image. The listing shows both tags with the same image id: a tag is only a label, not a copy.

**What the output means:** The build prints the new image id (sha256:...). The listing then shows tags demo and demo-copy with the same IMAGE ID, next to 1.1.0 and latest.

**What I will tell the professor:** "I built and tagged an image; two tags can point at the same image."

## Step 6 - Run a container with a port and a volume [video 02:38]

**What I am doing:** running

```powershell
docker run -d --name hotel-demo-app -p 18000:8000 -e SECRET_KEY=demo-only-not-a-real-secret -v hotel-demo-data:/data hotel-booking-app:demo | Out-Null; Start-Sleep 14; docker ps --filter name=hotel-demo-app --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'; curl.exe -s http://localhost:18000/health
```

**Spoken script (as in the video):**

> Now I run a container from that image. Dash d runs it in the background. Dash p maps port 18000 on my computer to port 8000 inside the container. The environment variable gives the secret key, and the dash v option mounts a named volume at slash data, where the database lives. After a few seconds Docker shows the container as healthy, and the health address answers with the demo version and the commit.

**What the output means:** Status 'Up ... (healthy)', the port mapping 0.0.0.0:18000->8000/tcp, and JSON with status ok, version 1.1.0-demo and the commit id.

**What I will tell the professor:** "A container started from my image answers on the mapped port and reports the version I built."

## Step 7 - Inspect the container [video 03:09]

**What I am doing:** running

```powershell
docker inspect hotel-demo-app --format 'state={{.State.Status}} health={{.State.Health.Status}} restart-policy={{.HostConfig.RestartPolicy.Name}} image={{.Config.Image}}'; docker inspect hotel-demo-app --format 'ports: {{json .NetworkSettings.Ports}}'; docker inspect hotel-demo-app --format '{{range .Mounts}}volume {{.Name}} -> {{.Destination}}{{end}}'
```

**Spoken script (as in the video):**

> Docker inspect shows everything about a container. I ask for a few facts: the state is running, the health is healthy, the image it came from, and the restart policy. A container started with docker run has no restart policy. Compose adds unless stopped. Then the port mapping and the volume: my named volume is mounted at slash data.

**What the output means:** state=running health=healthy restart-policy=no image=hotel-booking-app:demo; the port 8000/tcp mapped to host port 18000; volume hotel-demo-data -> /data.

**What I will tell the professor:** "Inspect shows the state, health, port mapping and the persistent volume of the container."

## Step 8 - Logs [video 03:37]

**What I am doing:** running

```powershell
docker logs --tail 10 hotel-demo-app
```

**Spoken script (as in the video):**

> Docker logs shows what the application printed. Here are the last lines: Gunicorn starting its workers, then the access log lines, including the health checks that Docker itself makes every ten seconds. Logs are the first place to look when a container misbehaves.

**What the output means:** Gunicorn start-up lines and request log lines for /health.

**What I will tell the professor:** "Logs are the first place to look when a container behaves badly."

## Step 9 - Stop, start and restart [video 03:59]

**What I am doing:** running

```powershell
docker stop hotel-demo-app | Out-Null; docker ps -a --filter name=hotel-demo-app --format '{{.Names}}: {{.Status}}'; docker start hotel-demo-app | Out-Null; Start-Sleep 14; docker ps --filter name=hotel-demo-app --format '{{.Names}}: {{.Status}}'; docker restart hotel-demo-app | Out-Null; 'restarted with docker restart'
```

**Spoken script (as in the video):**

> The lifecycle. Docker stop sends a polite signal and the container exits. Its status is Exited. The container still exists, with its data. Docker start brings the same container back, and after a few seconds the health check passes again. Docker restart does both in one command.

**What the output means:** First 'Exited (0)...', then 'Up ... (healthy)' after start, then the restart confirmation.

**What I will tell the professor:** "A stopped container still exists and can be started again with its data."

## Step 10 - Persistent storage: writing data [video 04:31]

**What I am doing:** running

```powershell
docker exec hotel-demo-app python -c "import sqlite3; c = sqlite3.connect('/data/hotel.db'); c.execute('INSERT INTO users (email, full_name, password_hash) VALUES (?, ?, ?)', ('persist@example.com', 'Persist Test', 'x')); c.commit(); print('users in database:', c.execute('SELECT COUNT(*) FROM users').fetchone()[0])"
```

**Spoken script (as in the video):**

> Does the data survive? Not automatically. It survives only because of the volume. First I write a row into the real SQLite database inside the container, a test user, and read back the number of users: one.

**What the output means:** users in database: 1

**What I will tell the professor:** "I wrote a row into the database file that lives in the volume."

## Step 11 - Persistent storage: remove the container, keep the data [video 04:50]

**What I am doing:** running

```powershell
docker rm -f hotel-demo-app | Out-Null; docker run -d --name hotel-demo-app2 -p 18000:8000 -e SECRET_KEY=demo-only-not-a-real-secret -v hotel-demo-data:/data hotel-booking-app:demo | Out-Null; Start-Sleep 12; docker exec hotel-demo-app2 python -c "import sqlite3; print('users after the old container was deleted:', sqlite3.connect('/data/hotel.db').execute('SELECT COUNT(*) FROM users').fetchone()[0])"
```

**Spoken script (as in the video):**

> Now I delete the container completely, with remove dash f. Its writable layer is gone. Then I start a brand new container from the same image and the same volume. When I count the users again, the row is still there: users, one. The data lives in the volume, not in the container, which is why Compose can replace containers during a deployment without losing bookings.

**What the output means:** users after the old container was deleted: 1 - the data survived because it is stored in the volume.

**What I will tell the professor:** "Deleting and recreating the container keeps the data, because the database lives in a named volume."

## Step 12 - Clean up the demo objects [video 05:23]

**What I am doing:** running

```powershell
docker rm -f hotel-demo-app2 | Out-Null; docker volume rm hotel-demo-data | Out-Null; docker rmi hotel-booking-app:demo hotel-booking-app:demo-copy | Out-Null; 'demo containers left: ' + (docker ps -a --filter name=hotel-demo --format '{{.Names}}' | Measure-Object).Count; docker volume ls --format '{{.Name}}' | Select-String 'hotel'
```

**Spoken script (as in the video):**

> Finally, I remove everything the demo created: the container, the volume and the two demo tags. Then I list what is left: no demo containers, and the project's real volumes, like the staging and production data and Jenkins, are untouched.

**What the output means:** 'demo containers left: 0' and the project's own volumes (hotel-prod_hotel-data, hotel-staging_hotel-data, hotel-jenkins_..., hotel-ansible-lab_...).

**What I will tell the professor:** "The demo cleaned up after itself; the real deployments and their data were not touched."
