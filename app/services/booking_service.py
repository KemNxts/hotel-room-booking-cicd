from datetime import date

from app.models import BookingStatus

from .errors import BookingError, NotFoundError


class BookingService:
    def __init__(self, booking_dao, room_dao, max_nights=30, today=date.today):
        self.bookings = booking_dao
        self.rooms = room_dao
        self.max_nights = max_nights
        # `today` is a function, not a value, so tests can freeze the date
        # (e.g. today=lambda: date(2030, 1, 1)) and stay deterministic.
        self.today = today

    # ---------- validation ----------

    def validate_stay(self, check_in, check_out):
        """Turn the two date strings from a form into validated date objects."""
        try:
            ci = date.fromisoformat(check_in or "")
            co = date.fromisoformat(check_out or "")
        except ValueError:
            raise BookingError("Please choose valid check-in and check-out dates.") from None

        if ci < self.today():
            raise BookingError("Check-in date cannot be in the past.")
        if co <= ci:
            raise BookingError("Check-out must be after check-in.")
        if (co - ci).days > self.max_nights:
            raise BookingError(f"A booking can be at most {self.max_nights} nights.")
        return ci, co

    # ---------- feature 2: availability ----------

    def search_rooms(self, check_in, check_out):
        """Return [(room, is_available), ...] for every room for the given dates."""
        ci, co = self.validate_stay(check_in, check_out)
        booked = self.bookings.booked_room_ids(ci, co)
        return [(room, room.id not in booked) for room in self.rooms.list_all()]

    def list_rooms(self):
        return self.rooms.list_all()

    # ---------- feature 3: booking request ----------

    def request_booking(self, user_id, room_id, check_in, check_out):
        """Create a PENDING booking. Returns the new Booking."""
        ci, co = self.validate_stay(check_in, check_out)
        try:
            room = self.rooms.find_by_id(int(room_id))
        except (TypeError, ValueError):
            room = None
        if room is None:
            raise BookingError("That room does not exist.")

        total = (co - ci).days * room.price_per_night
        booking_id = self.bookings.create_if_room_free(user_id, room.id, ci, co, total)
        if booking_id is None:
            raise BookingError(
                f"Room {room.room_number} is no longer available for those dates."
            )
        return self.bookings.find_by_id(booking_id)

    # ---------- features 4, 5, 6: confirm, cancel, track ----------

    def get_booking(self, booking_id, user_id):
        """Return the booking if it exists AND belongs to this user."""
        booking = self.bookings.find_by_id(booking_id)
        # Someone else's booking is reported as "not found" rather than
        # "forbidden", so users cannot probe which booking ids exist.
        if booking is None or booking.user_id != user_id:
            raise NotFoundError("Booking not found.")
        return booking

    def list_bookings(self, user_id):
        return self.bookings.list_for_user(user_id)

    def confirm_booking(self, booking_id, user_id):
        booking = self.get_booking(booking_id, user_id)
        if not booking.can_confirm:
            raise BookingError(f"Only pending bookings can be confirmed (this one is {booking.status}).")
        if not self.bookings.update_status(booking.id, BookingStatus.CONFIRMED,
                                           [BookingStatus.PENDING]):
            raise BookingError("Booking changed in the meantime, please reload.")
        return self.bookings.find_by_id(booking.id)

    def cancel_booking(self, booking_id, user_id):
        booking = self.get_booking(booking_id, user_id)
        if not booking.can_cancel:
            raise BookingError("This booking is already cancelled.")
        if not self.bookings.update_status(booking.id, BookingStatus.CANCELLED,
                                           list(BookingStatus.ACTIVE)):
            raise BookingError("Booking changed in the meantime, please reload.")
        return self.bookings.find_by_id(booking.id)
