"""Gunicorn settings (read by: gunicorn --config gunicorn.conf.py wsgi:app)."""
import os

# Listen on all interfaces inside the container; Nginx connects to app:8000.
bind = "0.0.0.0:8000"

# Worker processes. Each one handles one request at a time. 2 is plenty for
# a demo; a common rule of thumb is (2 x CPU cores) + 1.
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))

# Kill and replace a worker that is stuck on one request for over 30 s.
timeout = 30

# "-" = write logs to stdout/stderr, so `docker logs` shows them.
accesslog = "-"
errorlog = "-"
