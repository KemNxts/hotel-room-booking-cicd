"""Take report screenshots of the RUNNING system with Selenium.

Real screenshots of real pages - nothing is mocked. Run from the repo root:

    python scripts/capture_screenshots.py --app http://localhost:8082
    python scripts/capture_screenshots.py --app http://localhost:8082 \
        --jenkins http://localhost:8090 --jenkins-password <admin password>

Creates a new guest account and a few bookings in the target app (unique
email, dates far in the future). Output: docs/evidence/screenshots/*.png
"""
import argparse
import random
import time
import uuid
from datetime import date, timedelta
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

OUT = Path("docs/evidence/screenshots")


def browser(width=1280, height=900):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument(f"--window-size={width},{height}")
    return webdriver.Chrome(options=options)


def wait_for(drv, by, value, timeout=15):
    return WebDriverWait(drv, timeout).until(EC.visibility_of_element_located((by, value)))


def shot(drv, name):
    OUT.mkdir(parents=True, exist_ok=True)
    # Make the page's viewport as tall as the page (Chrome DevTools command),
    # so the whole page - including the footer - is in the screenshot.
    height = drv.execute_script("return document.documentElement.scrollHeight")
    drv.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
        "width": 1280, "height": max(600, min(height, 2400)), "deviceScaleFactor": 1, "mobile": False})
    time.sleep(0.5)  # let the page re-layout at the new size
    drv.save_screenshot(str(OUT / f"{name}.png"))
    drv.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
    print("saved", OUT / f"{name}.png")


def search(drv, app, check_in, check_out):
    drv.get(f"{app}/rooms")
    for field_id, value in (("check_in", check_in), ("check_out", check_out)):
        drv.execute_script("arguments[0].value = arguments[1];", drv.find_element(By.ID, field_id), value)
    drv.find_element(By.ID, "search-btn").click()
    wait_for(drv, By.ID, "availability-table")


def book_first_free(drv):
    drv.find_element(By.CSS_SELECTOR, "button[id^='book-']").click()
    wait_for(drv, By.ID, "booking-status")


def capture_app(app):
    drv = browser()
    try:
        start = date.today() + timedelta(days=random.randint(300, 900))
        # (days after start, nights): one stay to confirm, one left pending, one to cancel.
        stays = [(start + timedelta(days=d), start + timedelta(days=d + n))
                 for d, n in ((0, 3), (10, 2), (20, 1))]

        drv.get(f"{app}/rooms")
        shot(drv, "app-01-rooms")

        drv.get(f"{app}/register")
        drv.find_element(By.ID, "full_name").send_keys("Demo Guest")
        drv.find_element(By.ID, "email").send_keys(f"demo-{uuid.uuid4().hex[:6]}@example.com")
        drv.find_element(By.ID, "password").send_keys("password123")
        shot(drv, "app-02-register")
        drv.find_element(By.ID, "register-btn").click()
        wait_for(drv, By.ID, "nav-user")

        search(drv, app, stays[0][0].isoformat(), stays[0][1].isoformat())
        shot(drv, "app-03-availability")
        book_first_free(drv)
        shot(drv, "app-04-booking-pending")
        drv.find_element(By.ID, "confirm-btn").click()
        wait_for(drv, By.CSS_SELECTOR, ".flash")
        shot(drv, "app-05-booking-confirmed")

        # Two more bookings: one stays pending, one gets cancelled.
        search(drv, app, stays[1][0].isoformat(), stays[1][1].isoformat())
        book_first_free(drv)
        search(drv, app, stays[2][0].isoformat(), stays[2][1].isoformat())
        book_first_free(drv)
        drv.find_element(By.ID, "cancel-btn").click()
        wait_for(drv, By.CSS_SELECTOR, ".flash")
        shot(drv, "app-06-booking-cancelled")

        drv.get(f"{app}/bookings")
        wait_for(drv, By.ID, "bookings-table")
        shot(drv, "app-07-my-bookings-status")
    finally:
        drv.quit()


def capture_jenkins(jenkins, password, job="hotel-booking"):
    drv = browser()
    try:
        drv.get(f"{jenkins}/login")
        wait_for(drv, By.NAME, "j_username").send_keys("admin")
        drv.find_element(By.NAME, "j_password").send_keys(password)
        drv.find_element(By.NAME, "Submit").click()
        wait_for(drv, By.ID, "page-header")

        drv.get(f"{jenkins}/job/{job}/")
        WebDriverWait(drv, 20).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, "table, .stage-view, #pipeline-box"))
        shot(drv, "jenkins-01-job-stage-view")

        # Last build and the deliberately failing build #2 (defect demo).
        last = drv.execute_script(
            "return fetch(arguments[0]).then(r => r.json()).then(j => j.lastBuild.number)",
            f"{jenkins}/job/{job}/api/json")
        for number, name in ((last, "jenkins-02-last-build"), (2, "jenkins-04-build2-defect")):
            drv.get(f"{jenkins}/job/{job}/{number}/")
            wait_for(drv, By.ID, "main-panel")
            shot(drv, name)
        drv.get(f"{jenkins}/job/{job}/{last}/testReport/")
        wait_for(drv, By.ID, "main-panel")
        shot(drv, "jenkins-03-last-build-tests")
        drv.get(f"{jenkins}/job/{job}/2/testReport/")
        wait_for(drv, By.ID, "main-panel")
        shot(drv, "jenkins-05-build2-failed-test")
    finally:
        drv.quit()


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--app", help="Base URL of the running portal")
    parser.add_argument("--jenkins", help="Base URL of Jenkins")
    parser.add_argument("--jenkins-password", help="Jenkins admin password")
    args = parser.parse_args()
    if args.app:
        capture_app(args.app.rstrip("/"))
    if args.jenkins:
        capture_jenkins(args.jenkins.rstrip("/"), args.jenkins_password)


if __name__ == "__main__":
    main()
