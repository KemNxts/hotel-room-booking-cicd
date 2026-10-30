# Task 11 - viva questions and answers

**Task 11 - Docker Image and Container Lifecycle**

Source: section G of [task-11-docker-image-and-container-lifecycle.md](../../task-11-docker-image-and-container-lifecycle.md) - answers checked against the
repository and the evidence in this project.

1. **Image vs container?** An image is the read-only package; a container is a running instance of it. Many containers can run from one image.
2. **Why copy `requirements.txt` before the code?** Docker caches each layer;
   dependencies are reinstalled only when `requirements.txt` changes, not on every code change.
3. **Why a non-root user?** If the app were compromised, the attacker would not be root inside the container (`whoami` shows `appuser`).
4. **How is the app configured?** Environment variables (`APP_ENV`,
   `SECRET_KEY`, `DATABASE_PATH`...); no secrets are in the image.
5. **What does the HEALTHCHECK do?** Every 10 s it requests `/health`; Docker
   marks the container healthy/unhealthy, and compose starts Nginx only when the app is healthy.
6. **What is port mapping?** `-p 8095:8000` connects port 8095 on the host to 8000 in the container.
7. **(Project-specific) How did you prove data persistence?** I created an
   account, deleted the container, started a new one on the same volume and
   logged in with that account - HTTP 302 success (2026-10-20).
8. **(Project-specific) Why Gunicorn and Nginx?** Gunicorn runs the Python app
   with several workers; Nginx is the only public entry point and serves CSS
   directly. The app port isn't even published in compose.
9. **What does `.dockerignore` do?** Keeps files like `.git`, `.venv`, tests,
   docs and `.env` out of the build context - smaller images, no secrets.
10. **`docker stop` vs `docker rm`?** Stop ends the process (container still
    exists, can start again); rm deletes the container (volume kept).
11. **What happens to data with `docker compose down -v`?** `-v` also deletes the volume - the database is lost. Plain `down` keeps it.

## Extra questions that match this demonstration

1. **Does the booking data survive when the container is deleted?**
   Yes, but only because the database file lives in a named Docker volume mounted at /data. In the video I add a row, delete the container, start a new container with the same volume, and the row is still there. A container started without that volume would start with an empty database.

2. **How does the application access the database in Docker?**
   It is SQLite, a single file. The image sets DATABASE_PATH=/data/hotel.db and declares /data as a volume; Compose mounts the named volume hotel-data there. There is no separate database server.
