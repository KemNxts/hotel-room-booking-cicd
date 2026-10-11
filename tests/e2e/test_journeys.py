"""Critical user journeys, driven through a real browser.

Tests use unique emails and dates far in the future, and pick whichever room
is free rather than a fixed one, so they also work against a long-running
deployment (E2E_BASE_URL) where earlier runs left data behind.
"""
import random
import uuid
from datetime import date, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PASSWORD = "password123"
# Random far-future window per test session, to avoid clashing with old data.
_SESSION_OFFSET = random.randint(200, 2000)


# ------------------------------------------------------------------ helpers

def wait(driver, condition, timeout=10):
    return WebDriverWait(driver, timeout).until(condition)


def stay(days_from_offset, nights=2):
    """ISO check-in/check-out strings, unique to this test session."""
    start = date.today() + timedelta(days=_SESSION_OFFSET + days_from_offset)
    return start.isoformat(), (start + timedelta(days=nights)).isoformat()


def unique_email(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def flash_text(driver):
    return wait(driver, EC.visibility_of_element_located((By.CSS_SELECTOR, ".flash"))).text


def register(driver, base_url, name, email):
    driver.get(f"{base_url}/register")
    driver.find_element(By.ID, "full_name").send_keys(name)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "register-btn").click()
    wait(driver, EC.visibility_of_element_located((By.ID, "nav-user")))


def logout(driver):
    driver.find_element(By.ID, "logout-btn").click()
    wait(driver, EC.visibility_of_element_located((By.ID, "nav-login")))


def search(driver, base_url, check_in, check_out):
    driver.get(f"{base_url}/rooms")
    # <input type="date"> typing depends on the OS locale (dd/mm vs mm/dd),
    # so we set the value with JavaScript, then submit the real form.
    for field_id, value in (("check_in", check_in), ("check_out", check_out)):
        el = driver.find_element(By.ID, field_id)
        driver.execute_script("arguments[0].value = arguments[1];", el, value)
    driver.find_element(By.ID, "search-btn").click()
    wait(driver, EC.visibility_of_element_located((By.ID, "availability-table")))


def book_first_free_room(driver):
    """Click the first Book button; return (room_number, booking_id)."""
    button = driver.find_element(By.CSS_SELECTOR, "button[id^='book-']")
    room_number = button.get_attribute("id").removeprefix("book-")
    button.click()
    wait(driver, EC.visibility_of_element_located((By.ID, "booking-status")))
    booking_id = driver.current_url.rstrip("/").rsplit("/", 1)[-1]
    return room_number, booking_id


def status(driver):
    return driver.find_element(By.ID, "booking-status").text


# ----------------------------------------------------------------- journeys

def test_journey_1_register_new_guest(driver, base_url):
    register(driver, base_url, "Asha Guest", unique_email("asha"))

    assert driver.find_element(By.ID, "nav-user").text == "Asha Guest"
    assert "account has been created" in flash_text(driver)
    assert driver.current_url.endswith("/rooms")


def test_journey_2_login_rejects_wrong_password_then_accepts_right_one(driver, base_url):
    email = unique_email("ravi")
    register(driver, base_url, "Ravi Guest", email)
    logout(driver)

    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys("not-my-password")
    driver.find_element(By.ID, "login-btn").click()
    assert "Invalid email or password" in flash_text(driver)
    assert not driver.find_elements(By.ID, "nav-user")  # still logged out

    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "login-btn").click()
    wait(driver, EC.visibility_of_element_located((By.ID, "nav-user")))
    assert "Welcome back" in flash_text(driver)


def test_journey_3_search_request_and_confirm_booking(driver, base_url):
    register(driver, base_url, "Meera Guest", unique_email("meera"))
    check_in, check_out = stay(0, nights=2)

    search(driver, base_url, check_in, check_out)
    assert driver.find_elements(By.CSS_SELECTOR, ".badge-ok"), "expected at least one free room"

    book_first_free_room(driver)
    assert status(driver) == "PENDING"
    assert driver.find_element(By.ID, "booking-check-in").text == check_in
    assert driver.find_element(By.ID, "booking-check-out").text == check_out

    driver.find_element(By.ID, "confirm-btn").click()
    wait(driver, EC.text_to_be_present_in_element((By.ID, "booking-status"), "CONFIRMED"))
    assert "Booking confirmed" in flash_text(driver)
    assert not driver.find_elements(By.ID, "confirm-btn")  # can't confirm twice


def test_journey_4_cancel_booking_and_track_status(driver, base_url):
    register(driver, base_url, "Kiran Guest", unique_email("kiran"))
    search(driver, base_url, *stay(10, nights=3))
    _, booking_id = book_first_free_room(driver)
    driver.find_element(By.ID, "confirm-btn").click()
    wait(driver, EC.text_to_be_present_in_element((By.ID, "booking-status"), "CONFIRMED"))

    driver.find_element(By.ID, "cancel-btn").click()
    wait(driver, EC.text_to_be_present_in_element((By.ID, "booking-status"), "CANCELLED"))
    assert "Booking cancelled" in flash_text(driver)
    assert not driver.find_elements(By.ID, "cancel-btn")

    # Status tracking: My bookings shows the up-to-date status.
    driver.find_element(By.ID, "nav-my-bookings").click()
    row = wait(driver, EC.visibility_of_element_located((By.ID, f"booking-row-{booking_id}")))
    assert "CANCELLED" in row.text


def test_journey_5_booked_room_is_unavailable_to_another_guest(driver, base_url):
    check_in, check_out = stay(20, nights=2)

    register(driver, base_url, "First Guest", unique_email("first"))
    search(driver, base_url, check_in, check_out)
    room_number, _ = book_first_free_room(driver)
    logout(driver)

    register(driver, base_url, "Second Guest", unique_email("second"))
    search(driver, base_url, check_in, check_out)

    row = driver.find_element(By.ID, f"room-{room_number}")
    assert "Booked" in row.text
    assert not driver.find_elements(By.ID, f"book-{room_number}")
