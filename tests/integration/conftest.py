"""Fixtures for integration tests: the whole Flask app (controllers +
services + DAOs + a real SQLite file), driven through Flask's test client.
Faster than a browser, but covers HTTP details the unit tests cannot:
redirects, status codes, sessions, CSRF and per-user access control."""
from datetime import date, timedelta

import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    # A brand-new database file per test, so tests never affect each other.
    return create_app({"APP_ENV": "test", "SECRET_KEY": "integration-test-key",
                       "DATABASE_PATH": str(tmp_path / "it.db")})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def stay():
    """A valid two-night stay well in the future (the app uses the real 'today' here)."""
    check_in = date.today() + timedelta(days=200)
    return check_in.isoformat(), (check_in + timedelta(days=2)).isoformat()
