"""SQLite connection handling.

One connection per HTTP request, stored on Flask's `g` object and closed
automatically when the request ends.
"""
import sqlite3
from contextlib import contextmanager
from importlib import resources

from flask import current_app, g


def connect(path):
    """Open a connection configured the way the rest of the app expects."""
    # isolation_level=None = autocommit mode: every statement commits on its
    # own, and we open transactions explicitly only where we need them
    # (see immediate_transaction below). This keeps transaction control visible.
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row             # rows behave like dicts: row["email"]
    conn.execute("PRAGMA foreign_keys = ON")   # SQLite does not enforce FKs by default
    return conn


def get_db():
    """Return this request's connection, opening it on first use."""
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE_PATH"])
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(path):
    """Create tables and seed demo rooms. Safe to call on every start-up."""
    schema = resources.files("app").joinpath("schema.sql").read_text(encoding="utf-8")
    conn = connect(path)
    try:
        conn.executescript(schema)
    finally:
        conn.close()


@contextmanager
def immediate_transaction(conn):
    """Run a block of SQL as one transaction that holds the write lock.

    BEGIN IMMEDIATE takes SQLite's write lock at the *start*, so two users
    booking the same room at the same moment are processed one after the
    other: the second one sees the first one's booking and is rejected.
    """
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
