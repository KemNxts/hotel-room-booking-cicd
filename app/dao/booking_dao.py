from app.db import immediate_transaction
from app.models import Booking, BookingStatus

# Two stays overlap when each one starts before the other one ends.
# Touching stays do NOT overlap: check-out on the 5th and a new check-in on
# the 5th is fine. Only PENDING/CONFIRMED bookings block a room.
_OVERLAP_SQL = """
    check_in < :check_out
    AND check_out > :check_in
    AND status IN ('PENDING', 'CONFIRMED')
"""

# Bookings are always shown with their room number and type.
_SELECT_WITH_ROOM = """
    SELECT b.*, r.room_number, r.room_type
    FROM bookings b JOIN rooms r ON r.id = b.room_id
"""


class BookingDao:
    def __init__(self, conn):
        self.conn = conn

    def booked_room_ids(self, check_in, check_out):
        """Ids of rooms that already have an active booking overlapping the dates."""
        rows = self.conn.execute(
            f"SELECT DISTINCT room_id FROM bookings WHERE {_OVERLAP_SQL}",
            {"check_in": check_in.isoformat(), "check_out": check_out.isoformat()},
        ).fetchall()
        return {r["room_id"] for r in rows}

    def create_if_room_free(self, user_id, room_id, check_in, check_out, total_price):
        """Insert a PENDING booking only if the room is still free.

        The overlap check and the insert run inside one locked transaction so
        two people cannot book the same room for the same night.
        Returns the new booking id, or None if the room was already taken.
        """
        params = {
            "user_id": user_id,
            "room_id": room_id,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "total_price": total_price,
            "status": BookingStatus.PENDING,
        }
        with immediate_transaction(self.conn):
            clash = self.conn.execute(
                f"SELECT 1 FROM bookings WHERE room_id = :room_id AND {_OVERLAP_SQL} LIMIT 1",
                params,
            ).fetchone()
            if clash:
                return None
            cur = self.conn.execute(
                """INSERT INTO bookings (user_id, room_id, check_in, check_out, total_price, status)
                   VALUES (:user_id, :room_id, :check_in, :check_out, :total_price, :status)""",
                params,
            )
            return cur.lastrowid

    def find_by_id(self, booking_id):
        row = self.conn.execute(
            f"{_SELECT_WITH_ROOM} WHERE b.id = ?", (booking_id,)
        ).fetchone()
        return Booking.from_row(row) if row else None

    def list_for_user(self, user_id):
        rows = self.conn.execute(
            f"{_SELECT_WITH_ROOM} WHERE b.user_id = ? ORDER BY b.check_in DESC, b.id DESC",
            (user_id,),
        ).fetchall()
        return [Booking.from_row(r) for r in rows]

    def update_status(self, booking_id, new_status, allowed_current):
        """Change status only if the booking is currently in one of `allowed_current`.

        Putting the condition in the WHERE clause makes the check-and-update a
        single atomic statement. Returns True if a row was updated.
        """
        placeholders = ",".join("?" for _ in allowed_current)
        cur = self.conn.execute(
            f"""UPDATE bookings
                SET status = ?, updated_at = datetime('now')
                WHERE id = ? AND status IN ({placeholders})""",
            (new_status, booking_id, *allowed_current),
        )
        return cur.rowcount == 1
