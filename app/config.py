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
    }
