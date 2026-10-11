# Container Lifecycle

## Image vs container

- **Image** = a read-only template (our code + Python + dependencies), built
  from the `Dockerfile`. Like a class.
- **Container** = a running instance of an image, with its own thin writable
  layer on top. Like an object. Many containers can run from one image.
- **Volume** = storage managed by Docker that lives *outside* any container.
  Our SQLite database lives in the `hotel-data` volume, so deleting or
  replacing a container does not lose bookings.

## Lifecycle states

```
              docker create / run
  (image) ───────────────────────────> CREATED
                                          │ docker start
                                          v
              docker pause         ┌──> RUNNING ──┐  docker stop
   PAUSED <──────────────────────  │       │      │  (SIGTERM, then SIGKILL after 10s)
     │      docker unpause         │       │      v
     └─────────────────────────────┘       │    EXITED ── docker start ──> RUNNING
                                           │      │
                                           │      │ docker rm
                                           v      v
                                     (process crashes)  REMOVED
```

On top of the state, our `HEALTHCHECK` gives a **health status**:
`starting` -> `healthy` (GET /health works) or `unhealthy` (3 failures in a row).
`docker compose` waits for the app to be `healthy` before starting nginx.

`restart: unless-stopped` in `docker-compose.yml` means Docker restarts a
crashed container automatically, and after a server reboot, unless we
stopped it on purpose.

## Single container (app only, no nginx)

```bash
# Build the image (the tag = name:version); version info is baked in for /health
docker build -t hotel-booking-app:1.1.0 --build-arg APP_VERSION=1.1.0 --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) .
docker tag hotel-booking-app:1.1.0 hotel-booking-app:latest     # a second name for the same image

# Create + start a container in the background
docker run -d --name hotel-app \
  -p 8000:8000 \
  -e SECRET_KEY=<long-random-string> \
  -v hotel-data:/data \
  hotel-booking-app:1.1.0
# -> http://localhost:8000   (-p HOST:CONTAINER = port mapping)

docker ps                         # running containers (STATUS shows health)
docker logs -f hotel-app          # follow Gunicorn logs (Ctrl+C to stop following)
docker exec -it hotel-app sh      # open a shell inside the running container
docker inspect --format '{{.State.Health.Status}}' hotel-app
docker port hotel-app             # which host port maps to 8000
docker image inspect -f '{{json .Config.Labels}}' hotel-booking-app:1.1.0   # version + commit labels

docker stop hotel-app             # RUNNING -> EXITED (graceful shutdown)
docker start hotel-app            # EXITED -> RUNNING (same container, same data)
docker restart hotel-app
docker rm -f hotel-app            # remove the container (volume is kept)

docker volume ls                  # hotel-data is still there
docker volume rm hotel-data       # deletes the database for real
docker image ls                   # list images
docker image prune                # delete unused dangling images
```

## Full stack (nginx + app) with Docker Compose

```bash
cp .env.example .env              # Windows: copy .env.example .env
# edit .env and set SECRET_KEY

docker compose up -d --build      # build both images, create network + volume, start
docker compose ps                 # state + health of each service
docker compose logs -f app        # app logs
docker compose restart app        # restart one service
docker compose down               # stop + remove containers and network (volume kept)
docker compose down -v            # ... and delete the database volume too
```

App: http://localhost:8080 (change with `HOST_PORT` in `.env`).

## Updating to a new version (what the pipeline does)

1. `docker build` creates new images tagged `<VERSION>-<commit>`, e.g.
   `1.1.0-d07929b`, and `docker push` stores them in the registry.
2. `docker compose up -d` sees the image changed and **re-creates** the
   container: stop old -> remove old -> create new -> start new.
3. The new container mounts the same `hotel-data` volume, so data survives.
4. `--wait` + the health check confirm the new version works and is the
   expected version; if not, the pipeline fails.

## Rollback

Old images stay in the registry (and on the server), so rolling back is just
running the previous tag - no rebuild, the exact image that was tested before:

```bash
# shell variables SECRET_KEY, APP_ENV, HOST_PORT, IMAGE_PREFIX as for the deploy
IMAGE_TAG=1.0.0-661751d docker compose up -d --no-build --wait   # back to v1.0.0
curl http://localhost:8082/health                                  # -> "version":"1.0.0"
```

On servers managed by Ansible: `ansible-playbook rollback.yml` (see
[07-ansible.md](07-ansible.md)).

Limitation: containers are re-created, so there is a few seconds' gap
(no zero-downtime claim). Database changes are not rolled back - fine here
because no release changed the schema.

## Genuine evidence

- [evidence/docker/lifecycle.txt](evidence/docker/lifecycle.txt): build, tag,
  image labels, volume, run with port mapping, health, logs, inspect, non-root
  user, stop -> Exited, start, restart, `rm -f`, a NEW container on the same
  volume where the account registered earlier can still log in, clean-up.
- [evidence/docker/rollback-prod.txt](evidence/docker/rollback-prod.txt): prod
  rolled back 1.1.0 -> 1.0.0 and forward again, verified with `/health`.
