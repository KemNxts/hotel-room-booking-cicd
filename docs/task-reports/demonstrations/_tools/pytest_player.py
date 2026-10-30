"""pytest plugin: run the project's REAL Selenium tests in a VISIBLE, slowed-down Chrome
so that they can be screen-recorded and explained.

    python -m pytest -p pytest_player tests/e2e/test_journeys.py      (PYTHONPATH = this folder)

Nothing in the tests is changed or skipped. The plugin only
  * opens ONE visible Chrome window for the whole run (the tests' `driver`
    fixture gets that window instead of starting a headless one; its quit()
    just clears the cookies and moves to a blank page);
  * pauses after every click / typed character and outlines the element about
    to be clicked, so a viewer can follow;
  * shows the narration step (title + caption) at the bottom of the page and
    waits for the voice-over of each step to finish before the next test starts.

It is driven by environment variables set by record-demo.ps1:
    DEMO_STEPS, DEMO_TIMING, DEMO_GO, DEMO_LOG, DEMO_TITLE
Each step either has "test": "<pytest test name>" or is a stand-alone talking step.
"""
import json
import os
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from browser_player import CAPTION_JS, now_ms

STEPS = []
TIMING = []
S = {"idx": 0, "go_ms": 0, "log": [], "driver": None, "step_start": 0, "cmd_end": 0,
     "caption": None, "real_quit": None, "outcomes": {}}


def _env(name):
    return os.environ[name]


def _caption(title, text):
    S["caption"] = (title, text)
    drv = S["driver"]
    if drv is None:
        return
    try:
        drv.execute_script(
            "try{sessionStorage.setItem('demoCaption', arguments[0]);}catch(e){}"
            "if(window.__demoBuild){window.__demoBuild();}",
            json.dumps({"title": title, "text": text}))
    except Exception:
        pass


def _begin(i):
    s = STEPS[i]
    S["step_start"] = now_ms()
    S["idx"] = i
    _caption(f"STEP {i + 1} of {len(STEPS)}  -  {s['title']}", s.get("caption", ""))
    time.sleep(1.2)


def _end(i, outcome=None):
    s = STEPS[i]
    audio_ms = int(TIMING[i]["audioMs"])
    cmd_end = now_ms()
    pause = int(float(s.get("pauseAfter", 2.5)) * 1000)
    time.sleep((max(0, audio_ms - (now_ms() - S["step_start"])) + pause) / 1000.0)
    S["log"].append({"index": i, "title": s["title"], "startMs": S["step_start"] - S["go_ms"],
                     "cmdEndMs": cmd_end - S["go_ms"], "endMs": now_ms() - S["go_ms"],
                     "audioMs": audio_ms, "outcome": outcome or ""})


def _step_for(test_name):
    for i, s in enumerate(STEPS):
        if s.get("test") == test_name:
            return i
    return None


def pytest_configure(config):
    global STEPS, TIMING
    STEPS = json.loads(Path(_env("DEMO_STEPS")).read_text(encoding="utf-8-sig"))["steps"]
    TIMING = json.loads(Path(_env("DEMO_TIMING")).read_text(encoding="utf-8-sig"))
    if isinstance(TIMING, dict):
        TIMING = [TIMING]

    # --- slow, visible interaction (applies to every element the tests touch)
    orig_click, orig_keys, orig_clear = WebElement.click, WebElement.send_keys, WebElement.clear

    def click(self):
        try:
            self.parent.execute_script(
                "arguments[0].scrollIntoView({block:'center'});"
                "arguments[0].style.outline='4px solid #ff2d55';arguments[0].style.outlineOffset='3px';", self)
        except Exception:
            pass
        time.sleep(0.9)
        orig_click(self)
        time.sleep(0.7)

    def send_keys(self, *value):
        try:
            self.parent.execute_script("arguments[0].style.outline='4px solid #ff2d55';", self)
        except Exception:
            pass
        for chunk in value:
            for ch in str(chunk):
                orig_keys(self, ch)
                time.sleep(0.04)
        time.sleep(0.3)

    def clear(self):
        orig_clear(self)
        time.sleep(0.2)

    WebElement.click, WebElement.send_keys, WebElement.clear = click, send_keys, clear

    # --- one shared visible Chrome for the whole run
    real_chrome = webdriver.Chrome
    opts = webdriver.ChromeOptions()
    opts.add_argument("--window-size=1280,860")
    opts.add_argument("--window-position=20,20")
    # Software rendering: ffmpeg's window capture cannot read a GPU-composited Chrome window (it records black).
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-gpu-compositing")
    opts.add_argument("--disable-direct-composition")
    opts.add_argument("--no-first-run")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-notifications")
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("prefs", {"credentials_enable_service": False,
                                           "profile.password_manager_enabled": False})
    drv = real_chrome(options=opts)
    drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": CAPTION_JS})
    S["real_quit"] = drv.quit
    S["driver"] = drv
    drv.quit = lambda: None          # the tests' fixture calls quit(); keep the window

    orig_get = drv.get

    def get(url):
        orig_get(url)
        if S["caption"]:
            _caption(*S["caption"])

    drv.get = get

    def factory(*args, **kwargs):
        # every test's `driver` fixture gets the same window, with a clean session
        try:
            drv.delete_all_cookies()
        except Exception:
            pass
        return drv

    webdriver.Chrome = factory

    title = _env("DEMO_TITLE")
    orig_get("data:text/html,<title>%s</title><body style='background:%%23111;color:%%23eee;"
             "font:28px Segoe UI;padding:40px'>Starting demo...</body>" % title)

    go = Path(_env("DEMO_GO"))
    while not go.exists():
        time.sleep(0.1)
    S["go_ms"] = now_ms()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    i = _step_for(item.name)
    if i is None:
        return
    # pending talking steps that sit before this test's step
    while S["idx"] < i:
        j = S["idx"]
        _begin(j)
        _end(j)
        S["idx"] = j + 1
    _begin(i)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    outcome = yield
    i = _step_for(item.name)
    if i is not None:
        S["cmd_end"] = now_ms()
        failed = outcome.excinfo is not None
        S["outcomes"][item.name] = "FAILED" if failed else "PASSED"
        _end(i, S["outcomes"][item.name])
        S["idx"] = i + 1


def pytest_sessionfinish(session, exitstatus):
    # remaining stand-alone steps (closing remarks), then write the log
    while S["idx"] < len(STEPS) and not STEPS[S["idx"]].get("test"):
        j = S["idx"]
        _begin(j)
        _end(j)
        S["idx"] = j + 1
    total = now_ms() - S["go_ms"]
    Path(_env("DEMO_LOG")).write_text(
        json.dumps({"goEpochMs": S["go_ms"], "totalMs": total, "steps": S["log"],
                    "pytestExit": int(exitstatus)}, indent=2), encoding="utf-8")
    time.sleep(2.5)   # keep the window open until the recorder has stopped
    try:
        S["real_quit"]()
    except Exception:
        pass
