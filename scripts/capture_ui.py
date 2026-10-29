"""Screenshot every customer-facing page at mobile, tablet and desktop sizes.

Starts the real app on a free port with a throw-away database, walks the
whole guest journey in headless Chrome and saves full-page screenshots.
It also measures horizontal overflow on every page and prints a summary,
so layout problems are found by measurement, not only by eye.

    python scripts/capture_ui.py                      # -> docs/ui-evidence/after/
    python scripts/capture_ui.py --out docs/ui-evidence/before --sizes desktop
"""
import argparse
import sys
import tempfile
import threading
import time
import uuid
from datetime import date, timedelta
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import create_app  # noqa: E402

SIZES = {"mobile": (375, 812), "tablet": (768, 1024), "desktop": (1440, 900)}


class Shooter:
    def __init__(self, drv, out, size_name):
        self.drv, self.out, self.size_name = drv, out, size_name
        self.width, self.height = SIZES[size_name]
        self.overflow = []

    def viewport(self, height):
        self.drv.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
            "width": self.width, "height": height, "deviceScaleFactor": 1,
            "mobile": self.size_name == "mobile"})

    def shot(self, name):
        self.viewport(self.height)
        time.sleep(0.3)
        scroll_w = self.drv.execute_script("return document.documentElement.scrollWidth")
        if scroll_w > self.width:
            self.overflow.append(f"{name}: page is {scroll_w}px wide in a {self.width}px viewport")
        page_h = self.drv.execute_script("return document.documentElement.scrollHeight")
        self.viewport(max(self.height, min(page_h, 4000)))
        time.sleep(0.3)
        self.out.mkdir(parents=True, exist_ok=True)
        path = self.out / f"{self.size_name}-{name}.png"
        self.drv.save_screenshot(str(path))
        print("saved", path)


def wait_for(drv, by, value, timeout=10):
    return WebDriverWait(drv, timeout).until(EC.visibility_of_element_located((by, value)))


def set_dates(drv, check_in, check_out):
    for field_id, value in (("check_in", check_in), ("check_out", check_out)):
        drv.execute_script("arguments[0].value = arguments[1];", drv.find_element(By.ID, field_id), value)


def search(drv, base, check_in, check_out):
    drv.get(f"{base}/rooms")
    set_dates(drv, check_in, check_out)
    drv.find_element(By.ID, "search-btn").click()
    wait_for(drv, By.ID, "availability-table")


def register(drv, base, name, password="password123"):
    drv.get(f"{base}/register")
    drv.find_element(By.ID, "full_name").send_keys(name)
    drv.find_element(By.ID, "email").send_keys(f"{uuid.uuid4().hex[:8]}@example.com")
    drv.find_element(By.ID, "password").send_keys(password)
    drv.find_element(By.ID, "register-btn").click()
    # present, not visible: on phones the account name is inside the closed menu
    WebDriverWait(drv, 10).until(EC.presence_of_element_located((By.ID, "nav-user")))


def logout(drv):
    btn = drv.find_elements(By.ID, "logout-btn")
    if btn and btn[0].is_displayed():
        btn[0].click()
    else:  # mobile: open the menu first
        drv.find_element(By.CSS_SELECTOR, "[data-nav-toggle]").click()
        wait_for(drv, By.ID, "logout-btn").click()
    WebDriverWait(drv, 10).until(EC.presence_of_element_located((By.ID, "nav-login")))


def journey(drv, base, s):
    start = date.today() + timedelta(days=60)
    stay = (start.isoformat(), (start + timedelta(days=3)).isoformat())

    drv.get(f"{base}/rooms")
    s.shot("01-home")
    toggle = drv.find_element(By.CSS_SELECTOR, "[data-nav-toggle]")
    if toggle.is_displayed():                       # phones/tablets: open the menu
        toggle.click()
        wait_for(drv, By.ID, "nav-login")
        s.shot("01b-menu-open")
        toggle.click()

    # Keyboard: Tab from the top of the login page must show a visible focus ring.
    drv.get(f"{base}/login")
    body = drv.find_element(By.TAG_NAME, "body")
    for _ in range(4):
        body = drv.switch_to.active_element
        body.send_keys(Keys.TAB)
    s.shot("01c-keyboard-focus")

    # Another guest books two rooms first, so the results show both states.
    register(drv, base, "Other Guest")
    for _ in range(2):
        search(drv, base, *stay)
        drv.find_element(By.CSS_SELECTOR, "button[id^='book-']").click()
        wait_for(drv, By.ID, "booking-status")
    logout(drv)

    search(drv, base, *stay)
    s.shot("02-availability-logged-out")

    drv.get(f"{base}/register")
    s.shot("03-register")
    drv.find_element(By.ID, "full_name").send_keys("Asha Rao")
    drv.find_element(By.ID, "email").send_keys("not-an-email@x")
    drv.find_element(By.ID, "password").send_keys("password123")
    drv.find_element(By.ID, "register-btn").click()
    wait_for(drv, By.CSS_SELECTOR, ".flash")
    s.shot("04-register-error")

    drv.get(f"{base}/login")
    drv.find_element(By.ID, "email").send_keys("nobody@example.com")
    drv.find_element(By.ID, "password").send_keys("wrong-password")
    drv.find_element(By.ID, "login-btn").click()
    wait_for(drv, By.CSS_SELECTOR, ".flash")
    s.shot("05-login-error")

    register(drv, base, "Asha Rao")
    search(drv, base, *stay)
    s.shot("06-availability-logged-in")

    drv.get(f"{base}/bookings")
    s.shot("07-my-bookings-empty")

    search(drv, base, *stay)
    drv.find_element(By.CSS_SELECTOR, "button[id^='book-']").click()
    wait_for(drv, By.ID, "booking-status")
    s.shot("08-booking-requested")
    drv.find_element(By.ID, "confirm-btn").click()
    WebDriverWait(drv, 10).until(EC.text_to_be_present_in_element((By.ID, "booking-status"), "CONFIRMED"))
    s.shot("09-booking-confirmed")

    later = (start + timedelta(days=20), start + timedelta(days=22))
    search(drv, base, later[0].isoformat(), later[1].isoformat())
    drv.find_element(By.CSS_SELECTOR, "button[id^='book-']").click()
    wait_for(drv, By.ID, "booking-status")
    drv.find_element(By.ID, "cancel-btn").click()
    confirm = drv.find_elements(By.ID, "cancel-confirm-btn")
    if confirm:
        wait_for(drv, By.ID, "cancel-confirm-btn")
        s.shot("10-cancel-dialog")
        # Accessibility: the safe choice has focus, and Escape closes without cancelling.
        assert drv.switch_to.active_element.text == "Keep booking", "focus should start on 'Keep booking'"
        drv.switch_to.active_element.send_keys(Keys.ESCAPE)
        WebDriverWait(drv, 5).until(EC.invisibility_of_element_located((By.ID, "cancel-confirm-btn")))
        assert drv.find_element(By.ID, "booking-status").text == "PENDING", "Escape must not cancel"
        drv.find_element(By.ID, "cancel-btn").click()
        wait_for(drv, By.ID, "cancel-confirm-btn").click()
    WebDriverWait(drv, 10).until(EC.text_to_be_present_in_element((By.ID, "booking-status"), "CANCELLED"))
    s.shot("11-booking-cancelled")

    search(drv, base, (start + timedelta(days=40)).isoformat(), (start + timedelta(days=41)).isoformat())
    drv.find_element(By.CSS_SELECTOR, "button[id^='book-']").click()
    wait_for(drv, By.ID, "booking-status")
    drv.get(f"{base}/bookings")
    s.shot("12-my-bookings")

    drv.get(f"{base}/rooms?check_in=2020-01-05&check_out=2020-01-01")
    s.shot("13-search-error")
    drv.get(f"{base}/no-such-page")
    s.shot("14-not-found")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default="docs/ui-evidence/after")
    parser.add_argument("--sizes", default="mobile,tablet,desktop")
    args = parser.parse_args()

    problems = []
    for size_name in args.sizes.split(","):
        # A fresh app + database per screen size, so every run starts from the
        # same state (otherwise earlier runs would have booked all the rooms).
        db = Path(tempfile.mkdtemp()) / "ui.db"
        app = create_app({"APP_ENV": "test", "SECRET_KEY": "ui-capture", "DATABASE_PATH": str(db),
                          "APP_VERSION": "1.1.0"})
        server = make_server("127.0.0.1", 0, app, threaded=True)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}"

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,1000")
        drv = webdriver.Chrome(options=options)
        try:
            shooter = Shooter(drv, Path(args.out), size_name)
            journey(drv, base, shooter)
            problems += [f"[{size_name}] {p}" for p in shooter.overflow]
        finally:
            drv.quit()
            server.shutdown()

    print("\nHorizontal overflow check:", "none found" if not problems else "")
    for p in problems:
        print("  ", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
