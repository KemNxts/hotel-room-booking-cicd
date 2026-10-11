"""Fixtures for Selenium end-to-end tests.

- base_url: starts the real Flask app in a background thread on a free port
  with a throw-away database. Set E2E_BASE_URL to test an already-running
  deployment instead (e.g. the Docker container after a deploy).
- driver: a Chrome browser (headless by default; HEADLESS=0 to watch it).
  If a test fails, a screenshot and the page HTML are saved to
  reports/screenshots/ so you can see what the browser saw.
"""
import os
import re
import threading
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from werkzeug.serving import make_server

from app import create_app

SCREENSHOT_DIR = Path("reports") / "screenshots"


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    external = os.environ.get("E2E_BASE_URL")
    if external:
        yield external.rstrip("/")
        return

    db_file = tmp_path_factory.mktemp("e2e") / "e2e.db"
    app = create_app({"DATABASE_PATH": str(db_file), "APP_ENV": "test",
                      "SECRET_KEY": "e2e-test-key"})
    # Port 0 = let the OS pick any free port, so parallel CI jobs don't clash.
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture
def driver(request):
    options = webdriver.ChromeOptions()
    if os.environ.get("HEADLESS", "1") != "0":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    # Needed when Chrome runs as root inside Linux containers / CI agents.
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # On a CI agent with distro Chromium (see deploy/jenkins/Dockerfile) we are
    # told where the browser and driver are. Otherwise Selenium Manager (built
    # into Selenium 4) finds Chrome and downloads a matching chromedriver.
    service = None
    if os.environ.get("CHROME_BIN"):
        options.binary_location = os.environ["CHROME_BIN"]
    if os.environ.get("CHROMEDRIVER"):
        service = Service(executable_path=os.environ["CHROMEDRIVER"])
    drv = webdriver.Chrome(options=options, service=service)
    drv.implicitly_wait(0)  # we use explicit waits (WebDriverWait) instead
    yield drv

    report = getattr(request.node, "rep_call", None)
    if report is not None and report.failed:
        _save_failure_artifacts(drv, request.node.name)
    drv.quit()


def _save_failure_artifacts(drv, test_name):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w.-]", "_", test_name)
    drv.save_screenshot(str(SCREENSHOT_DIR / f"{safe}.png"))
    (SCREENSHOT_DIR / f"{safe}.html").write_text(drv.page_source, encoding="utf-8")
    print(f"\n[e2e] failure screenshot saved: {SCREENSHOT_DIR / (safe + '.png')}")


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Store each phase's result on the test item (item.rep_setup / rep_call /
    rep_teardown) so the driver fixture can tell whether the test failed."""
    report = yield
    setattr(item, f"rep_{report.when}", report)
    return report


def pytest_collection_modifyitems(items):
    """Tag every test in this folder with the `e2e` marker automatically."""
    for item in items:
        if "e2e" in Path(str(item.fspath)).parts:
            item.add_marker(pytest.mark.e2e)
