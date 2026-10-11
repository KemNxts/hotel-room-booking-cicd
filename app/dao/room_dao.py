from app.models import Room


class RoomDao:
    def __init__(self, conn):
        self.conn = conn

    def list_all(self):
        rows = self.conn.execute(
            "SELECT * FROM rooms ORDER BY room_number"
        ).fetchall()
        return [Room.from_row(r) for r in rows]

    def find_by_id(self, room_id):
        row = self.conn.execute(
            "SELECT * FROM rooms WHERE id = ?", (room_id,)
        ).fetchone()
        return Room.from_row(row) if row else None
