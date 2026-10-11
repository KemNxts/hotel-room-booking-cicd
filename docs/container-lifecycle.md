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
# Build the image (the tag = name:version)
docker build -t hotel-booking-app:1.0 .

# Create + start a container in the background
docker run -d --name hotel-app \
  -p 8000:8000 \
  -e SECRET_KEY=<long-random-string> \
  -v hotel-data:/data \
  hotel-booking-app:1.0
# -> http://localhost:8000

docker ps                         # running containers (STATUS shows health)
docker logs -f hotel-app          # follow Gunicorn logs (Ctrl+C to stop following)
docker exec -it hotel-app sh      # open a shell inside the running container
docker inspect --format '{{.State.Health.Status}}' hotel-app

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

1. `docker build` creates a new image with a new tag (the Jenkins build number).
2. `docker compose up -d` sees the image changed and **re-creates** the
   container: stop old -> remove old -> create new -> start new.
3. The new container mounts the same `hotel-data` volume, so data survives.
4. The health check confirms the new version works; if it does not, the
   pipeline fails, and we can roll back by deploying the previous tag:
   `IMAGE_TAG=<previous-build-number> docker compose up -d --no-build`.
