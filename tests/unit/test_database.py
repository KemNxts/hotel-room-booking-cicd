"""Rules the database itself enforces (schema.sql), independent of the
service layer: seeding is repeatable and double booking is impossible even
for code that writes to the tables directly."""
import sqlite3

import pytest

from app.db import connect, init_db

INSERT_BOOKING = """INSERT INTO bookings
    (user_id, room_id, check_in, check_out, total_price, status)
    VALUES (?, ?, ?, ?, 1000, ?)"""


@pytest.fixture
def raw(conn, user, room_101):
    """Helper that inserts bookings with plain SQL, bypassing the service."""
    def insert(check_in, check_out, status="PENDING", room_id=room_101.id):
        return conn.execute(INSERT_BOOKING, (user.id, room_id, check_in, check_out, status)).lastrowid
    return insert


def test_init_db_can_run_repeatedly_without_duplicating_rooms(db_path):
    init_db(db_path)  # second and third start-up of the app
    init_db(db_path)
    conn = connect(db_path)
    try:
        assert conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0] == 6
    finally:
        conn.close()


def test_trigger_rejects_overlapping_insert(raw):
    raw("2030-01-10", "2030-01-13")
    with pytest.raises(sqlite3.IntegrityError, match="already booked"):
        raw("2030-01-12", "2030-01-14")


def test_trigger_allows_back_to_back_and_cancelled(raw):
    raw("2030-01-10", "2030-01-13")
    raw("2030-01-13", "2030-01-15")                    # starts on the other's check-out day
    raw("2030-01-11", "2030-01-12", status="CANCELLED")  # cancelled rows never block


def test_trigger_rejects_reactivating_a_cancelled_booking_into_a_clash(conn, raw):
    old = raw("2030-01-10", "2030-01-13", status="CANCELLED")
    raw("2030-01-10", "2030-01-13")
    with pytest.raises(sqlite3.IntegrityError, match="already booked"):
        conn.execute("UPDATE bookings SET status = 'PENDING' WHERE id = ?", (old,))


@pytest.mark.parametrize("check_in, check_out, status", [
    ("2030-01-13", "2030-01-10", "PENDING"),   # check-out before check-in
    ("2030-01-10", "2030-01-10", "PENDING"),   # zero nights
    ("2030-01-10", "2030-01-12", "UNKNOWN"),   # status outside the state machine
])
def test_check_constraints_reject_inconsistent_rows(raw, check_in, check_out, status):
    with pytest.raises(sqlite3.IntegrityError):
        raw(check_in, check_out, status=status)


def test_foreign_keys_reject_unknown_room(raw):
    with pytest.raises(sqlite3.IntegrityError):
        raw("2030-01-10", "2030-01-12", room_id=9999)
