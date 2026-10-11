"""Application configuration.

All settings come from environment variables so the same code (and the same
Docker image) can run in dev, test and prod with different values. Nothing
secret is hard-coded for production.
"""
import os

DEV_SECRET_KEY = "dev-only-change-me"


def load_config():
    """Read settings from the environment at app start-up (not at import time)."""
    return {
        # Which environment we are running in: dev | test | staging | prod.
        "APP_ENV": os.environ.get("APP_ENV", "dev"),
        # Signs the session cookie. The default is only for local development;
        # create_app refuses to start in prod without a real SECRET_KEY.
        "SECRET_KEY": os.environ.get("SECRET_KEY", DEV_SECRET_KEY),
        # Path of the SQLite file. None -> <instance folder>/hotel.db
        "DATABASE_PATH": os.environ.get("DATABASE_PATH"),
        # Business rule: longest stay allowed in one booking.
        "MAX_NIGHTS": int(os.environ.get("MAX_NIGHTS", "30")),
        # Which release is running. Baked into the Docker image at build time
        # and reported by /health, so a deploy or rollback can be verified.
        "APP_VERSION": os.environ.get("APP_VERSION", "dev"),
        "GIT_COMMIT": os.environ.get("GIT_COMMIT", "unknown"),
        # Session cookie protection. HttpOnly: JavaScript cannot read the
        # cookie. SameSite=Lax: the browser does not send it with form posts
        # from other sites. Secure (HTTPS only) is switched on with an env var
        # because the local demo runs on plain HTTP.
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": os.environ.get("SESSION_COOKIE_SECURE", "0") == "1",
    }
