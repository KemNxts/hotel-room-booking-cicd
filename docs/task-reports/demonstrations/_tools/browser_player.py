"""Drive a VISIBLE Chrome through the real hotel app while a demo is recorded.

Counterpart of player.ps1 for browser demos. It uses the same inputs and the
same log format, so record-demo.ps1 can record either one:

    python browser_player.py --steps task-06-app-steps.json --timing timing.json
        --go go --log log.json --title HOTEL-DEMO-T06 --repo <project folder>

What it does (nothing is simulated):
  * starts the REAL Flask app in this process on a free port, with a
    throw-away SQLite database in the temp folder (your instance/hotel.db is
    never touched);
  * opens Chrome with Selenium (not headless) and performs the actions named
    by each step's "do" field, using the same element ids the project's own
    Selenium tests use;
  * shows the step title and a short caption at the bottom of every page and
    outlines each element just before it is clicked.
"""
import argparse
import json
import sys
import tempfile
import threading
import time
import uuid
from datetime import date, timedelta
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PASSWORD = "password123"
REPO = "."   # set from --repo in main()

CAPTION_JS = r"""
window.__demoBuild = function () {
  try {
    var raw = sessionStorage.getItem('demoCaption'); if (!raw) return;
    var c = JSON.parse(raw);
    var old = document.getElementById('demo-caption'); if (old) old.remove();
    var d = document.createElement('div'); d.id = 'demo-caption';
    d.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:2147483647;background:rgba(10,10,10,.93);' +
      'color:#fff;padding:12px 24px;font:20px/1.35 "Segoe UI",Arial,sans-serif;border-top:4px solid #ffd54a;pointer-events:none';
    var t = document.createElement('div'); t.style.cssText = 'color:#7fd8ff;font-weight:700;margin-bottom:4px'; t.textContent = c.title;
    var x = document.createElement('div'); x.style.cssText = 'color:#ffe27a'; x.textContent = c.text;
    d.appendChild(t); d.appendChild(x);
    (document.body || document.documentElement).appendChild(d);
    if (document.body) document.body.style.paddingBottom = '150px';
  } catch (e) {}
};
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', window.__demoBuild);
else window.__demoBuild();
"""


def now_ms():
    return int(time.time() * 1000)


class Demo:
    def __init__(self, base, drv):
        self.base, self.drv = base, drv
        self.w = WebDriverWait(drv, 15)
        today = date.today()
        self.d1 = (today + timedelta(days=45), today + timedelta(days=47))
        self.d2 = (today + timedelta(days=90), today + timedelta(days=93))
        self.first_email = f"asha-{uuid.uuid4().hex[:6]}@example.com"
        self.second_email = f"ben-{uuid.uuid4().hex[:6]}@example.com"
        self.first_room = None
        self.first_booking_id = None

    # ---- small helpers -------------------------------------------------
    def pause(self, s):
        time.sleep(s)

    def caption(self, title, text):
        payload = json.dumps({"title": title, "text": text})
        try:
            self.drv.execute_script(
                "try{sessionStorage.setItem('demoCaption', arguments[0]);}catch(e){}"
                "if(window.__demoBuild){window.__demoBuild();}", payload)
        except Exception:
            pass

    def go(self, path):
        self.drv.get(self.base + path)

    def see(self, by, value):
        return self.w.until(EC.visibility_of_element_located((by, value)))

    def hl(self, el, secs=0.8):
        self.drv.execute_script(
            "arguments[0].scrollIntoView({block:'center'});"
            "arguments[0].style.outline='4px solid #ff2d55';arguments[0].style.outlineOffset='3px';", el)
        time.sleep(secs)

    def type(self, element_id, text):
        el = self.see(By.ID, element_id)
        self.hl(el, 0.3)
        el.clear()
        for ch in text:
            el.send_keys(ch)
            time.sleep(0.04)

    def click(self, element_id):
        el = self.see(By.ID, element_id)
        self.hl(el, 0.9)
        el.click()

    def flash(self):
        return self.see(By.CSS_SELECTOR, ".flash").text

    def set_dates(self, d):
        for field_id, value in (("check_in", d[0].isoformat()), ("check_out", d[1].isoformat())):
            el = self.see(By.ID, field_id)
            self.hl(el, 0.4)
            self.drv.execute_script("arguments[0].value = arguments[1];", el, value)

    def search(self, d):
        self.go("/rooms")
        self.set_dates(d)
        self.click("search-btn")
        self.see(By.ID, "availability-table")

    def register(self, name, email):
        self.go("/register")
        self.type("full_name", name)
        self.type("email", email)
        self.type("password", PASSWORD)
        self.click("register-btn")
        self.see(By.ID, "nav-user")

    def login(self, email, password):
        self.type("email", email)
        self.type("password", password)
        self.click("login-btn")

    def logout(self):
        self.click("logout-btn")
        self.see(By.ID, "nav-login")

    # ---- the actions the steps refer to --------------------------------
    def open_home(self):
        self.go("/rooms")
        self.see(By.ID, "nav-login")
        self.pause(2.5)

    def register_first(self):
        self.register("Asha Guest", self.first_email)
        self.pause(2.5)

    def login_flow(self):
        self.logout()
        self.pause(1)
        self.login(self.first_email, "not-my-password")
        self.flash()
        self.pause(2.5)
        self.login(self.first_email, PASSWORD)
        self.see(By.ID, "nav-user")
        self.pause(2.5)

    def availability(self):
        self.search(self.d1)
        self.pause(3)

    def book(self):
        button = self.see(By.CSS_SELECTOR, "button[id^='book-']")
        self.first_room = button.get_attribute("id").removeprefix("book-")
        self.hl(button, 1.0)
        button.click()
        self.see(By.ID, "booking-status")
        self.first_booking_id = self.drv.current_url.rstrip("/").rsplit("/", 1)[-1]
        self.pause(3)

    def confirm(self):
        self.click("confirm-btn")
        self.w.until(EC.text_to_be_present_in_element((By.ID, "booking-status"), "CONFIRMED"))
        self.pause(3)

    def second_guest(self):
        self.logout()
        self.pause(0.5)
        self.register("Ben Guest", self.second_email)
        self.search(self.d1)
        row = self.see(By.ID, f"room-{self.first_room}")
        self.hl(row, 3.0)
        self.logout()
        self.login(self.first_email, PASSWORD)
        self.see(By.ID, "nav-user")
        self.pause(1.5)

    def second_booking_and_tracking(self):
        self.search(self.d2)
        button = self.see(By.CSS_SELECTOR, "button[id^='book-']")
        self.hl(button, 0.8)
        button.click()
        self.see(By.ID, "booking-status")
        self.pause(1.5)
        self.click("nav-my-bookings")
        self.see(By.ID, f"booking-row-{self.first_booking_id}")
        self.pause(3.5)

    def cancel_and_recheck(self):
        row = self.see(By.ID, f"booking-row-{self.first_booking_id}")
        link = row.find_element(By.CSS_SELECTOR, "a")
        self.hl(link, 0.8)
        link.click()
        self.click("cancel-btn")
        self.click("cancel-confirm-btn")
        self.w.until(EC.text_to_be_present_in_element((By.ID, "booking-status"), "CANCELLED"))
        self.pause(2.5)
        self.click("nav-my-bookings")
        row = self.see(By.ID, f"booking-row-{self.first_booking_id}")
        self.hl(row, 3.0)
        self.search(self.d1)
        self.hl(self.see(By.ID, f"room-{self.first_room}"), 3.0)

    def closing(self):
        self.go("/health")
        self.pause(3.5)

    # ---- generic, data-driven actions (used by the Jenkins demos) ----------
    @staticmethod
    def _password():
        """The Jenkins admin password, read from deploy/jenkins/.env at run time.
        It is never printed, logged, written to a file or typed visibly on screen."""
        for line in (Path(REPO) / "deploy" / "jenkins" / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("JENKINS_ADMIN_PASSWORD="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
        raise RuntimeError("JENKINS_ADMIN_PASSWORD not found in deploy/jenkins/.env")

    def _auth_header(self):
        import base64
        token = base64.b64encode(f"admin:{self._password()}".encode()).decode()
        return {"Authorization": f"Basic {token}"}

    def api(self, path):
        import urllib.request
        req = urllib.request.Request(self.base + path, headers=self._auth_header())
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))

    def login_jenkins(self):
        """Log in before the recording starts, so no password handling is ever on video."""
        self.go("/login")
        self.see(By.NAME, "j_username").send_keys("admin")
        self.drv.find_element(By.NAME, "j_password").send_keys(self._password())
        self.drv.find_element(By.NAME, "Submit").click()
        self.w.until(lambda d: "/login" not in d.current_url)

    def scroll_text(self, text, offset=140, mark=True):
        found = self.drv.execute_script(
            "var needle=arguments[0], off=arguments[1], mark=arguments[2];"
            "var w=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), n;"
            "while((n=w.nextNode())){var i=n.nodeValue.indexOf(needle); if(i>=0){"
            " var r=document.createRange(); r.setStart(n,i); r.setEnd(n,i+needle.length);"
            " var rect=r.getBoundingClientRect();"
            " window.scrollTo({top: window.scrollY+rect.top-off, behavior:'smooth'});"
            " if(mark){try{var m=document.createElement('mark');m.style.background='#ffe14d';m.style.color='#000';"
            "  r.surroundContents(m);}catch(e){}}"
            " return true;}}"
            "return false;", text, offset, mark)
        if not found:
            print(f"[browser_player] text not found on page: {text!r}", file=sys.stderr)
        time.sleep(1.2)

    def wait_build(self, job, min_number, timeout=420):
        """Wait until Jenkins build number >= min_number has finished; return its result."""
        end = time.time() + timeout
        while time.time() < end:
            data = self.api(f"/job/{job}/api/json?tree=lastBuild[number,building,result]")
            last = data.get("lastBuild") or {}
            if last.get("number", 0) >= min_number and not last.get("building", True):
                self.build_result = last.get("result")
                return self.build_result
            time.sleep(3)
        self.build_result = "TIMEOUT"
        return self.build_result

    def run_actions(self, actions):
        for a in actions:
            if "goto" in a:
                self.go(a["goto"])
            elif "pause" in a:
                time.sleep(float(a["pause"]))
            elif "scroll_text" in a:
                self.scroll_text(a["scroll_text"], a.get("offset", 140), a.get("mark", True))
            elif "scroll" in a:
                self.drv.execute_script("window.scrollBy({top: arguments[0], behavior:'smooth'});", a["scroll"])
                time.sleep(float(a.get("secs", 1.2)))
            elif "scroll_top" in a:
                self.drv.execute_script("window.scrollTo({top: 0, behavior:'smooth'});")
                time.sleep(1.0)
            elif "highlight" in a:
                el = self.see(By.CSS_SELECTOR, a["highlight"])
                self.hl(el, float(a.get("secs", 2)))
            elif "click" in a:
                el = self.see(By.CSS_SELECTOR, a["click"])
                self.hl(el, 0.9)
                el.click()
            elif "click_text" in a:
                xp = f"//*[self::a or self::button or self::span][contains(normalize-space(.), {json.dumps(a['click_text'])})]"
                el = self.w.until(EC.element_to_be_clickable((By.XPATH, xp)))
                self.hl(el, 0.9)
                el.click()
            elif "trigger_build" in a:
                job = a["trigger_build"]
                before = (self.api(f"/job/{job}/api/json?tree=lastBuild[number]").get("lastBuild") or {}).get("number", 0)
                self.go(f"/job/{job}/build?delay=0sec")
                self.pause(float(a.get("read_secs", 1.0)))   # time to read the parameter form
                # not the header's "Search" button, which is also type=submit
                submit = self.w.until(EC.visibility_of_element_located(
                    (By.XPATH, "//button[normalize-space(.)='Build']")))
                self.hl(submit, 1.2)
                submit.click()
                self.expected_build = before + 1
            elif "wait_build" in a:
                self.wait_build(a["wait_build"], getattr(self, "expected_build", 1), int(a.get("timeout", 420)))
            else:
                print(f"[browser_player] unknown action: {a}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", required=True)
    ap.add_argument("--timing", required=True)
    ap.add_argument("--go", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--repo", required=True)
    a = ap.parse_args()

    global REPO
    REPO = a.repo
    cfg = json.loads(Path(a.steps).read_text(encoding="utf-8-sig"))
    server = None
    if cfg.get("app", True):
        # the real hotel app on a free port with a throw-away database
        sys.path.insert(0, a.repo)
        from werkzeug.serving import make_server
        from app import create_app

        tmp = tempfile.mkdtemp(prefix="hotel-browser-demo-")
        app = create_app({"DATABASE_PATH": str(Path(tmp) / "demo.db"), "APP_ENV": "test",
                          "SECRET_KEY": "demo-key", "APP_VERSION": "demo"})
        server = make_server("127.0.0.1", 0, app, threaded=True)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}"
    else:
        base = cfg["baseUrl"].rstrip("/")   # e.g. a running Jenkins

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
    drv = webdriver.Chrome(options=opts)
    drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": CAPTION_JS})
    d = Demo(base, drv)
    if cfg.get("jenkinsLogin"):
        d.login_jenkins()            # before the title page, so it is never on video
    # The window title is how the recorder finds this window: "<title> - Google Chrome".
    drv.get("data:text/html,<title>%s</title><body style='background:%%23111;color:%%23eee;"
            "font:28px Segoe UI;padding:40px'>Starting demo...</body>" % a.title)

    demo_steps = cfg["steps"]
    timing = json.loads(Path(a.timing).read_text(encoding="utf-8-sig"))
    if isinstance(timing, dict):
        timing = [timing]

    while not Path(a.go).exists():
        time.sleep(0.1)
    go_ms = now_ms()
    log = []
    try:
        for i, s in enumerate(demo_steps):
            audio_ms = int(timing[i]["audioMs"])
            start = now_ms()
            title = f"STEP {i + 1} of {len(demo_steps)}  -  {s['title']}"
            d.caption(title, s.get("caption", ""))
            time.sleep(1.2)
            if s.get("do"):
                getattr(d, s["do"])()
                d.caption(title, s.get("caption", ""))   # pages may have reloaded
            if s.get("actions"):
                # actions are run one at a time so the caption is re-shown after every page load
                for act in s["actions"]:
                    d.run_actions([act])
                    d.caption(title, s.get("caption", ""))
            cmd_end = now_ms()
            pause = int(float(s.get("pauseAfter", 2.5)) * 1000)
            wait = max(0, audio_ms - (now_ms() - start)) + pause
            time.sleep(wait / 1000.0)
            log.append({"index": i, "title": s["title"], "startMs": start - go_ms,
                        "cmdEndMs": cmd_end - go_ms, "endMs": now_ms() - go_ms, "audioMs": audio_ms})
        total = now_ms() - go_ms
        Path(a.log).write_text(json.dumps({"goEpochMs": go_ms, "totalMs": total, "steps": log}, indent=2),
                               encoding="utf-8")
        time.sleep(2.5)   # keep the window open until the recorder has stopped
    finally:
        drv.quit()
        if server:
            server.shutdown()


if __name__ == "__main__":
    main()
