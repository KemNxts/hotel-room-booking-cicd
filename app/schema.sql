-- Database schema. "IF NOT EXISTS" makes it safe to run on every start-up.

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT    NOT NULL UNIQUE,
    full_name     TEXT    NOT NULL,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS rooms (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number     TEXT    NOT NULL UNIQUE,
    room_type       TEXT    NOT NULL,
    capacity        INTEGER NOT NULL,
    price_per_night INTEGER NOT NULL  -- whole rupees, avoids float rounding
);

-- Dates are stored as ISO strings (YYYY-MM-DD). ISO dates sort correctly as
-- text, so "<" and ">" comparisons in SQL work for overlap checks.
CREATE TABLE IF NOT EXISTS bookings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    room_id     INTEGER NOT NULL REFERENCES rooms(id),
    check_in    TEXT    NOT NULL,
    check_out   TEXT    NOT NULL,
    total_price INTEGER NOT NULL,
    status      TEXT    NOT NULL CHECK (status IN ('PENDING', 'CONFIRMED', 'CANCELLED')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    CHECK (check_out > check_in)
);

CREATE INDEX IF NOT EXISTS idx_bookings_room ON bookings(room_id, status);
CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);

-- Demo rooms. INSERT OR IGNORE + the UNIQUE room_number means re-running this
-- (e.g. several Gunicorn workers starting at once) never creates duplicates.
INSERT OR IGNORE INTO rooms (room_number, room_type, capacity, price_per_night) VALUES
    ('101', 'Single',   1, 2500),
    ('102', 'Single',   1, 2500),
    ('201', 'Double',   2, 4000),
    ('202', 'Double',   2, 4000),
    ('301', 'Deluxe',   3, 6500),
    ('401', 'Suite',    4, 9500);
