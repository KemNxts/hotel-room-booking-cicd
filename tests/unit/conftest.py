"""Shared fixtures for service-layer unit tests.

Every test gets its own brand-new SQLite file in pytest's tmp_path, so tests
never affect each other and never touch the real instance/hotel.db.
No Flask app or browser is needed: services are plain Python objects.
"""
from datetime import date

import pytest

from app.dao import BookingDao, RoomDao, UserDao
from app.db import connect, init_db
from app.services import AuthService, BookingService

# All booking tests pretend "today" is this date so results never depend on
# the day the pipeline runs.
FROZEN_TODAY = date(2030, 1, 1)


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)  # creates tables and the 6 demo rooms
    return path


@pytest.fixture
def conn(db_path):
    c = connect(db_path)
    yield c
    c.close()


@pytest.fixture
def auth_service(conn):
    return AuthService(UserDao(conn))


@pytest.fixture
def booking_service(conn):
    return BookingService(BookingDao(conn), RoomDao(conn),
                          max_nights=30, today=lambda: FROZEN_TODAY)


@pytest.fixture
def user(auth_service):
    return auth_service.register("guest@example.com", "Guest User", "password123")


@pytest.fixture
def other_user(auth_service):
    return auth_service.register("other@example.com", "Other User", "password123")


@pytest.fixture
def room_101(conn):
    """Seeded room 101: Single, 2500 per night."""
    return next(r for r in RoomDao(conn).list_all() if r.room_number == "101")
