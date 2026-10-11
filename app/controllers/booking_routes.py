"""Features 3-6: booking request, confirmation, cancellation, status tracking."""
from flask import (Blueprint, abort, current_app, flash, g, redirect, render_template, request,
                   url_for)

from app.services import BookingError, NotFoundError

from .helpers import booking_service, login_required

bp = Blueprint("bookings", __name__, url_prefix="/bookings")


@bp.get("")
@login_required
def my_bookings():
    """Feature 6: list of the user's bookings with their current status."""
    return render_template("my_bookings.html",
                           bookings=booking_service().list_bookings(g.user.id))


@bp.post("")
@login_required
def create():
    """Feature 3: booking request -> creates a PENDING booking."""
    form = request.form
    try:
        booking = booking_service().request_booking(
            g.user.id, form.get("room_id"), form.get("check_in"), form.get("check_out")
        )
    except BookingError as err:
        flash(str(err), "error")
        # Back to the search the user came from.
        return redirect(url_for("rooms.list_rooms",
                                check_in=form.get("check_in"), check_out=form.get("check_out")))
    current_app.logger.info("Booking %s requested: user_id=%s room=%s %s..%s",
                            booking.id, g.user.id, booking.room_number,
                            booking.check_in, booking.check_out)
    flash("Booking requested. Please review and confirm it below.", "success")
    return redirect(url_for("bookings.detail", booking_id=booking.id))


@bp.get("/<int:booking_id>")
@login_required
def detail(booking_id):
    try:
        booking = booking_service().get_booking(booking_id, g.user.id)
    except NotFoundError:
        abort(404)
    return render_template("booking_detail.html", booking=booking)


@bp.post("/<int:booking_id>/confirm")
@login_required
def confirm(booking_id):
    """Feature 4: PENDING -> CONFIRMED."""
    return _change_status(booking_service().confirm_booking, booking_id, "Booking confirmed.")


@bp.post("/<int:booking_id>/cancel")
@login_required
def cancel(booking_id):
    """Feature 5: PENDING/CONFIRMED -> CANCELLED."""
    return _change_status(booking_service().cancel_booking, booking_id, "Booking cancelled.")


def _change_status(action, booking_id, success_message):
    """Confirm and cancel work the same way, so they share this helper.
    `action` is the service method to call (confirm_booking or cancel_booking)."""
    try:
        booking = action(booking_id, g.user.id)
        current_app.logger.info("Booking %s is now %s (user_id=%s)",
                                booking.id, booking.status, g.user.id)
        flash(success_message, "success")
    except NotFoundError:
        abort(404)
    except BookingError as err:
        flash(str(err), "error")
    return redirect(url_for("bookings.detail", booking_id=booking_id))
