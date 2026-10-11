"""Features 2-6: availability, booking request, confirm, cancel, status tracking.

"Today" is frozen at 2030-01-01 (see conftest.FROZEN_TODAY).
"""
import threading
from datetime import date

import pytest

from app.dao import BookingDao
from app.db import connect
from app.models import BookingStatus
from app.services import BookingError, NotFoundError


def available_numbers(results):
    """[(room, is_available), ...] -> set of available room numbers."""
    return {room.room_number for room, ok in results if ok}


# ---------------------------------------------------------------- validation

class TestValidateStay:
    def test_valid_dates_are_parsed(self, booking_service):
        assert booking_service.validate_stay("2030-01-10", "2030-01-12") == (
            date(2030, 1, 10), date(2030, 1, 12))

    def test_check_in_today_is_allowed(self, booking_service):
        booking_service.validate_stay("2030-01-01", "2030-01-02")

    @pytest.mark.parametrize("check_in, check_out, message", [
        ("2029-12-31", "2030-01-02", "in the past"),
        ("2030-01-10", "2030-01-10", "after check-in"),   # zero nights
        ("2030-01-10", "2030-01-09", "after check-in"),   # reversed
        ("2030-01-01", "2030-02-01", "at most 30 nights"),  # 31 nights
        ("10/01/2030", "2030-01-12", "valid"),             # wrong format
        ("", "", "valid"),                                 # missing
    ])
    def test_invalid_stays_are_rejected(self, booking_service, check_in, check_out, message):
        with pytest.raises(BookingError, match=message):
            booking_service.validate_stay(check_in, check_out)

    def test_exactly_max_nights_is_allowed(self, booking_service):
        booking_service.validate_stay("2030-01-01", "2030-01-31")  # 30 nights


# -------------------------------------------------------------- availability

class TestSearchRooms:
    def test_all_rooms_free_when_no_bookings(self, booking_service):
        results = booking_service.search_rooms("2030-01-10", "2030-01-12")
        assert len(results) == 6
        assert all(ok for _room, ok in results)

    # Existing booking for room 101: 10th -> 13th (nights of 10, 11, 12).
    @pytest.mark.parametrize("check_in, check_out, room_101_free", [
        ("2030-01-08", "2030-01-10", True),   # ends the day the other starts
        ("2030-01-13", "2030-01-15", True),   # starts the day the other ends
        ("2030-01-09", "2030-01-11", False),  # overlaps the start
        ("2030-01-12", "2030-01-14", False),  # overlaps the end
        ("2030-01-11", "2030-01-12", False),  # fully inside
        ("2030-01-09", "2030-01-14", False),  # fully surrounds
    ])
    def test_overlap_rules(self, booking_service, user, room_101,
                           check_in, check_out, room_101_free):
        booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-13")

        free = available_numbers(booking_service.search_rooms(check_in, check_out))

        assert ("101" in free) is room_101_free
        assert len(free - {"101"}) == 5  # other rooms are never affected

    def test_cancelled_booking_frees_the_room(self, booking_service, user, room_101):
        b = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-13")
        booking_service.cancel_booking(b.id, user.id)

        free = available_numbers(booking_service.search_rooms("2030-01-10", "2030-01-13"))
        assert "101" in free

    def test_invalid_dates_raise(self, booking_service):
        with pytest.raises(BookingError):
            booking_service.search_rooms("2030-01-12", "2030-01-10")


# ----------------------------------------------------------- booking request

class TestRequestBooking:
    def test_creates_pending_booking_with_total_price(self, booking_service, user, room_101):
        booking = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-13")

        assert booking.status == BookingStatus.PENDING
        assert booking.user_id == user.id
        assert booking.room_number == "101"
        assert booking.nights == 3
        assert booking.total_price == 3 * 2500

    def test_room_id_from_a_form_string_is_accepted(self, booking_service, user, room_101):
        booking = booking_service.request_booking(user.id, str(room_101.id), "2030-01-10", "2030-01-11")
        assert booking.room_id == room_101.id

    @pytest.mark.parametrize("room_id", [9999, "abc", None])
    def test_unknown_room_is_rejected(self, booking_service, user, room_id):
        with pytest.raises(BookingError, match="does not exist"):
            booking_service.request_booking(user.id, room_id, "2030-01-10", "2030-01-11")

    def test_overlapping_booking_is_rejected(self, booking_service, user, other_user, room_101):
        booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-13")
        with pytest.raises(BookingError, match="no longer available"):
            booking_service.request_booking(other_user.id, room_101.id, "2030-01-12", "2030-01-14")

    def test_invalid_dates_are_rejected_before_anything_is_saved(self, booking_service, user, room_101):
        with pytest.raises(BookingError):
            booking_service.request_booking(user.id, room_101.id, "2029-12-01", "2029-12-03")
        assert booking_service.list_bookings(user.id) == []

    def test_simultaneous_requests_create_only_one_booking(self, db_path, user, room_101):
        """10 threads try to book the same room at the same instant.

        Each thread has its own DB connection (like separate Gunicorn workers).
        BEGIN IMMEDIATE serialises them, so exactly one must win.
        """
        start = threading.Barrier(10)
        results = []

        def attempt():
            conn = connect(db_path)
            try:
                start.wait()  # release all threads together
                results.append(BookingDao(conn).create_if_room_free(
                    user.id, room_101.id, date(2030, 1, 10), date(2030, 1, 12), 5000))
            finally:
                conn.close()

        threads = [threading.Thread(target=attempt) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        winners = [r for r in results if r is not None]
        assert len(results) == 10
        assert len(winners) == 1


# ------------------------------------------------- confirm / cancel / track

class TestConfirmBooking:
    def test_pending_becomes_confirmed(self, booking_service, user, room_101):
        b = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-11")
        assert booking_service.confirm_booking(b.id, user.id).status == BookingStatus.CONFIRMED

    def test_cannot_confirm_twice(self, booking_service, user, room_101):
        b = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-11")
        booking_service.confirm_booking(b.id, user.id)
        with pytest.raises(BookingError, match="Only pending"):
            booking_service.confirm_booking(b.id, user.id)

    def test_cannot_confirm_a_cancelled_booking(self, booking_service, user, room_101):
        b = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-11")
        booking_service.cancel_booking(b.id, user.id)
        with pytest.raises(BookingError, match="Only pending"):
            booking_service.confirm_booking(b.id, user.id)

    def test_other_user_cannot_confirm(self, booking_service, user, other_user, room_101):
        b = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-11")
        with pytest.raises(NotFoundError):
            booking_service.confirm_booking(b.id, other_user.id)
        assert booking_service.get_booking(b.id, user.id).status == BookingStatus.PENDING


class TestCancelBooking:
    def test_pending_can_be_cancelled(self, booking_service, user, room_101):
        b = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-11")
        assert booking_service.cancel_booking(b.id, user.id).status == BookingStatus.CANCELLED

    def test_confirmed_can_be_cancelled(self, booking_service, user, room_101):
        b = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-11")
        booking_service.confirm_booking(b.id, user.id)
        assert booking_service.cancel_booking(b.id, user.id).status == BookingStatus.CANCELLED

    def test_cannot_cancel_twice(self, booking_service, user, room_101):
        b = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-11")
        booking_service.cancel_booking(b.id, user.id)
        with pytest.raises(BookingError, match="already cancelled"):
            booking_service.cancel_booking(b.id, user.id)

    def test_other_user_cannot_cancel(self, booking_service, user, other_user, room_101):
        b = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-11")
        with pytest.raises(NotFoundError):
            booking_service.cancel_booking(b.id, other_user.id)
        assert booking_service.get_booking(b.id, user.id).status == BookingStatus.PENDING


class TestTracking:
    def test_get_missing_booking_raises_not_found(self, booking_service, user):
        with pytest.raises(NotFoundError):
            booking_service.get_booking(12345, user.id)

    def test_list_shows_only_own_bookings_with_current_status(
            self, booking_service, user, other_user, room_101):
        mine = booking_service.request_booking(user.id, room_101.id, "2030-01-10", "2030-01-11")
        booking_service.request_booking(other_user.id, room_101.id, "2030-01-20", "2030-01-21")
        booking_service.confirm_booking(mine.id, user.id)

        listed = booking_service.list_bookings(user.id)

        assert [b.id for b in listed] == [mine.id]
        assert listed[0].status == BookingStatus.CONFIRMED
