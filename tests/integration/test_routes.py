"""HTTP-level tests of every MVP route, the security rules and the health check."""
import re

import pytest

from app import create_app
from app.controllers.csrf import FORM_FIELD, SESSION_KEY


# ---------------------------------------------------------------- helpers

def post(client, url, follow_redirects=False, **data):
    """POST a form the way a browser would: with the session's CSRF token."""
    with client.session_transaction() as sess:
        token = sess.setdefault(SESSION_KEY, "test-csrf-token")
    return client.post(url, data={**data, FORM_FIELD: token}, follow_redirects=follow_redirects)


def register(client, email, name="Test Guest", password="password123"):
    return post(client, "/register", email=email, full_name=name, password=password)


def book(client, stay, room_id=1):
    """Request a booking and return its id (taken from the redirect URL)."""
    resp = post(client, "/bookings", room_id=room_id, check_in=stay[0], check_out=stay[1])
    assert resp.status_code == 302, resp.data
    location = resp.headers["Location"]
    assert location.startswith("/bookings/"), location
    return int(location.rsplit("/", 1)[1])


def status_of(client, booking_id):
    html = client.get(f"/bookings/{booking_id}").get_data(as_text=True)
    return re.search(r'id="booking-status">(\w+)<', html).group(1)


# ---------------------------------------------------------------- basics

def test_health_reports_status_env_and_version(client):
    data = client.get("/health").get_json()
    assert data["status"] == "ok"
    assert data["env"] == "test"
    assert "version" in data and "commit" in data


def test_home_redirects_to_rooms_and_lists_six_rooms(client):
    assert client.get("/").headers["Location"] == "/rooms"
    html = client.get("/rooms").get_data(as_text=True)
    assert html.count('data-testid="room-card"') == 6
    for number in ("101", "102", "201", "202", "301", "401"):
        assert f'<span class="plate__number">{number}</span>' in html


def test_unknown_page_returns_404(client):
    assert client.get("/no-such-page").status_code == 404


# ------------------------------------------------- feature 1: registration and login

def test_register_logs_the_user_in(client):
    resp = register(client, "new@example.com", name="Asha Rao")
    assert resp.status_code == 302
    assert "Asha Rao" in client.get("/rooms").get_data(as_text=True)


def test_invalid_registration_is_rejected_server_side(client):
    # The browser's "required"/"minlength" checks are bypassed here on purpose.
    resp = post(client, "/register", email="bad", full_name="", password="x")
    assert resp.status_code == 400


def test_login_wrong_then_right_password(client):
    register(client, "guest@example.com")
    post(client, "/logout")
    assert post(client, "/login", email="guest@example.com", password="wrong-pass").status_code == 401
    assert post(client, "/login", email="guest@example.com", password="password123").status_code == 302


def test_login_never_redirects_to_another_site(client):
    register(client, "guest@example.com")
    post(client, "/logout")
    resp = post(client, "/login?next=//evil.example/steal",
                email="guest@example.com", password="password123")
    assert resp.headers["Location"] == "/rooms"


def test_session_cookie_is_httponly_and_samesite(client):
    cookie = register(client, "cookie@example.com").headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie


# ------------------------------------------------- CSRF protection

def test_post_without_csrf_token_is_rejected(client):
    resp = client.post("/register", data={"email": "x@example.com", "full_name": "X",
                                          "password": "password123"})
    assert resp.status_code == 400


def test_post_with_wrong_csrf_token_is_rejected(client, stay):
    register(client, "guest@example.com")
    resp = client.post("/bookings", data={"room_id": 1, "check_in": stay[0],
                                          "check_out": stay[1], "csrf_token": "forged"})
    assert resp.status_code == 400
    assert "You have no bookings yet" in client.get("/bookings").get_data(as_text=True)


def test_forms_contain_the_csrf_token(client):
    assert 'name="csrf_token"' in client.get("/login").get_data(as_text=True)


# ------------------------------------------------- features 2-6

def test_anonymous_user_is_sent_to_login(client):
    resp = client.get("/bookings")
    assert resp.status_code == 302
    assert resp.headers["Location"].startswith("/login")


def test_availability_search_shows_booked_room(client, stay):
    register(client, "guest@example.com")
    book(client, stay, room_id=1)
    html = client.get(f"/rooms?check_in={stay[0]}&check_out={stay[1]}").get_data(as_text=True)
    card_101 = re.search(r'<article [^>]*id="room-101".*?</article>', html, re.S).group(0)
    card_102 = re.search(r'<article [^>]*id="room-102".*?</article>', html, re.S).group(0)
    assert "Booked" in card_101 and 'id="book-101"' not in card_101
    assert "Available" in card_102 and 'id="book-102"' in card_102


def test_invalid_search_dates_show_an_error(client):
    html = client.get("/rooms?check_in=2020-01-05&check_out=2020-01-01").get_data(as_text=True)
    assert "flash-error" in html


def test_full_lifecycle_request_confirm_cancel(client, stay):
    register(client, "guest@example.com")
    booking_id = book(client, stay)
    assert status_of(client, booking_id) == "PENDING"

    post(client, f"/bookings/{booking_id}/confirm")
    assert status_of(client, booking_id) == "CONFIRMED"

    post(client, f"/bookings/{booking_id}/cancel")
    assert status_of(client, booking_id) == "CANCELLED"

    # Feature 6: status tracking on the "My bookings" page.
    html = client.get("/bookings").get_data(as_text=True)
    assert f'id="booking-row-{booking_id}"' in html and "CANCELLED" in html


def test_repeated_cancellation_is_refused(client, stay):
    register(client, "guest@example.com")
    booking_id = book(client, stay)
    post(client, f"/bookings/{booking_id}/cancel")
    html = post(client, f"/bookings/{booking_id}/cancel", follow_redirects=True).get_data(as_text=True)
    assert "already cancelled" in html
    assert status_of(client, booking_id) == "CANCELLED"


def test_overlapping_request_for_same_room_is_refused(client, app, stay):
    register(client, "first@example.com")
    book(client, stay, room_id=1)

    second = app.test_client()
    register(second, "second@example.com")
    resp = post(second, "/bookings", follow_redirects=True,
                room_id=1, check_in=stay[0], check_out=stay[1])
    assert "no longer available" in resp.get_data(as_text=True)
    assert "You have no bookings yet" in second.get("/bookings").get_data(as_text=True)


def test_past_dates_cannot_be_booked(client):
    register(client, "guest@example.com")
    resp = post(client, "/bookings", follow_redirects=True,
                room_id=1, check_in="2020-01-01", check_out="2020-01-03")
    assert "cannot be in the past" in resp.get_data(as_text=True)


@pytest.mark.parametrize("url", ["/bookings/99999", "/bookings/abc"])
def test_invalid_booking_ids_return_404(client, url):
    register(client, "guest@example.com")
    assert client.get(url).status_code == 404


def test_other_users_cannot_see_confirm_or_cancel_my_booking(client, app, stay):
    register(client, "owner@example.com")
    booking_id = book(client, stay)

    intruder = app.test_client()
    register(intruder, "intruder@example.com")
    assert intruder.get(f"/bookings/{booking_id}").status_code == 404
    assert post(intruder, f"/bookings/{booking_id}/cancel").status_code == 404
    assert post(intruder, f"/bookings/{booking_id}/confirm").status_code == 404
    assert status_of(client, booking_id) == "PENDING"   # unchanged


# ------------------------------------------------- configuration safety

@pytest.mark.parametrize("key", ["", "dev-only-change-me"])
def test_prod_refuses_to_start_without_a_real_secret_key(tmp_path, key):
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({"APP_ENV": "prod", "SECRET_KEY": key,
                    "DATABASE_PATH": str(tmp_path / "p.db")})


def test_every_page_shows_hotel_contact_details(client):
    for url in ("/rooms", "/login", "/register"):
        assert 'id="hotel-contact"' in client.get(url).get_data(as_text=True)


def test_footer_shows_the_running_release(tmp_path):
    app = create_app({"APP_ENV": "test", "SECRET_KEY": "k", "APP_VERSION": "9.9.9",
                      "DATABASE_PATH": str(tmp_path / "f.db")})
    html = app.test_client().get("/rooms").get_data(as_text=True)
    assert 'id="app-version">Release 9.9.9 · test<' in html


def test_my_bookings_shows_number_of_nights(client, stay):
    register(client, "guest@example.com")
    book(client, stay)                                    # the stay fixture is 2 nights
    html = client.get("/bookings").get_data(as_text=True)
    assert "<th>Nights</th>" in html
    assert '<td class="nights">2</td>' in html
