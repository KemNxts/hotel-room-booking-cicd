from app.models import User


class UserDao:
    def __init__(self, conn):
        self.conn = conn

    def find_by_email(self, email):
        row = self.conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return User.from_row(row) if row else None

    def find_by_id(self, user_id):
        row = self.conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return User.from_row(row) if row else None

    def create(self, email, full_name, password_hash):
        """Insert a user and return the new id.

        Raises sqlite3.IntegrityError if the email already exists.
        """
        cur = self.conn.execute(
            "INSERT INTO users (email, full_name, password_hash) VALUES (?, ?, ?)",
            (email, full_name, password_hash),
        )
        return cur.lastrowid
