"""Shared helpers for the controllers: login guard and service construction."""
from functools import wraps

from flask import current_app, flash, g, redirect, request, url_for

from app.dao import BookingDao, RoomDao, UserDao
from app.db import get_db
from app.services import AuthService, BookingService


def auth_service():
    return AuthService(UserDao(get_db()))


def booking_service():
    conn = get_db()
    return BookingService(BookingDao(conn), RoomDao(conn),
                          max_nights=current_app.config["MAX_NIGHTS"])


def login_required(view):
    """Decorator: send anonymous users to the login page first."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Please log in first.", "error")
            # Remember where they were going so login can send them back.
            return redirect(url_for("auth.login", next=request.full_path))
        return view(*args, **kwargs)
    return wrapped


def safe_next_url(target):
    """Only follow `next` if it points inside this site (blocks open redirects
    like ?next=https://evil.example)."""
    # "//evil.example" and "/\evil.example" are treated by browsers as other sites.
    if target and target.startswith("/") and not target.startswith(("//", "/\\")):
        return target
    return url_for("rooms.list_rooms")
