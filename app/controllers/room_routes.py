"""Feature 2: room list and availability for a date range."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services import BookingError

from .helpers import booking_service

bp = Blueprint("rooms", __name__)


@bp.get("/")
def index():
    return redirect(url_for("rooms.list_rooms"))


@bp.get("/rooms")
def list_rooms():
    """Without dates: show all rooms. With ?check_in=&check_out=: show availability."""
    service = booking_service()
    check_in = request.args.get("check_in", "")
    check_out = request.args.get("check_out", "")

    results = None  # None = "no search yet"
    if check_in or check_out:
        try:
            results = service.search_rooms(check_in, check_out)
        except BookingError as err:
            flash(str(err), "error")

    return render_template(
        "rooms.html",
        rooms=service.list_rooms(),
        results=results,
        check_in=check_in,
        check_out=check_out,
    )
