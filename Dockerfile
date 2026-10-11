# Production image for the Flask app, served by Gunicorn.
# Build:  docker build -t hotel-booking-app .
FROM python:3.11-slim-bookworm

# PYTHONDONTWRITEBYTECODE: no .pyc files in the image.
# PYTHONUNBUFFERED: print logs immediately so `docker logs` is live.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=prod \
    DATABASE_PATH=/data/hotel.db

WORKDIR /app

# Install dependencies BEFORE copying the code. Docker caches each layer, so
# this slow step is only re-run when requirements.txt changes, not on every
# code change. Only runtime deps - no pytest/selenium in production.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY wsgi.py gunicorn.conf.py ./

# Run as an unprivileged user: if the app were ever compromised, the attacker
# is not root inside the container. /data holds the SQLite file.
# (Gunicorn keeps a small control socket in the user's home, so create one.)
RUN useradd --system --uid 1000 --create-home appuser \
    && mkdir /data && chown appuser /data
USER appuser

# Keep the database outside the container's writable layer so it survives
# container re-creation (mount a named volume here).
VOLUME /data

EXPOSE 8000

# Docker marks the container "healthy" only when /health answers. The slim
# image has no curl, so Python's standard library does the request.
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1

CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
