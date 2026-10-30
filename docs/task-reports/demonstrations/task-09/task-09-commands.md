# Task 9 - command sheet

**Task 9 - Selenium Test Design and Local Execution**

## Before you start

- The project `.venv` with Selenium and pytest, and Google Chrome installed. Selenium Manager downloads a matching chromedriver the first time (internet needed once).
- Nothing else needs to be running: the tests start the real Flask app themselves on a free port with a throw-away database.
- Open PowerShell in the project folder.
- Google Chrome installed; the project `.venv` with Selenium.
- To watch it yourself, without the recorder's slow motion: `$env:HEADLESS='0'; pytest tests/e2e -v` (a Chrome window opens and closes for each test).
- Do not touch the mouse or keyboard during the recording.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

### Task 9 (part 1) - Selenium test design: the code and a real headless run

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | Selenium and the five critical journeys | `Select-String -Path tests/e2e/test_journeys.py -Pattern '^def test_' \| ForEach-Object { $_.Line }` | Five test functions test_journey_1 to test_journey_5. |
| 2 | WebDriver: the browser fixture | `Get-Content tests/e2e/conftest.py \| Select-Object -Skip 43 -First 25` | The driver fixture: ChromeOptions, optional headless flag, window size, chromedriver service, implicitly_wait(0), yield, then failure artifacts and quit. |
| 3 | Test data: unique and independent | `Get-Content tests/e2e/test_journeys.py \| Select-Object -Skip 14 -First 19` | PASSWORD constant, a random session offset, wait helper, stay() for unique dates and unique_email() with a UUID. |
| 4 | Element locators | `Select-String -Path tests/e2e/test_journeys.py -Pattern '^def register' -Context 0,7 \| ForEach-Object { $_.Line; $_.Context.PostContext }` | register(): find_element(By.ID, ...) for each field, send_keys, click on register-btn, then a wait for nav-user. |
| 5 | Explicit waits | `Select-String -Path tests/e2e/*.py -Pattern 'WebDriverWait\|implicitly_wait\|EC\.' \| Select-Object -First 8 \| ForEach-Object { '{0}:{1}  {2}' -f $_.Filename, $_.LineNumber, $_.Line.Trim() }` | Lines using WebDriverWait, implicitly_wait(0) and expected_conditions such as visibility_of_element_located. |
| 6 | Assertions: what the test checks | `Select-String -Path tests/e2e/test_journeys.py -Pattern '^def test_journey_3' -Context 0,18 \| ForEach-Object { $_.Line; $_.Context.PostContext }` | The body of journey 3 with register, search, book, assert status == 'PENDING', date checks, confirm click, wait for CONFIRMED and assertions. |
| 7 | Failure screenshots | `Select-String -Path tests/e2e/conftest.py -Pattern '^def _save_failure' -Context 0,6 \| ForEach-Object { $_.Line; $_.Context.PostContext }; Get-ChildItem reports/screenshots \| Select-Object Name, Length, LastWriteTime \| Format-Table -AutoSize` | The _save_failure_artifacts function (save_screenshot + page_source) and the earlier failure png/html files with their timestamps. |
| 8 | Running the browser tests and reading the report | `pytest -m e2e -v --junitxml=reports/e2e-demo.xml; ([xml](Get-Content reports/e2e-demo.xml)).testsuites.testsuite \| Select-Object name, tests, failures, errors, skipped, time \| Format-List` | Five PASSED lines, '5 passed', then the XML summary with tests=5, failures=0, errors=0. |
| 9 | How Selenium tests differ from unit and integration tests | `foreach ($d in 'unit','integration','e2e') { '{0,-12} {1}' -f $d, (pytest tests/$d --collect-only -q \| Select-Object -Last 1) }` | unit: 59 tests, integration: 26 tests, e2e: 5 tests collected. |

### Task 9 (part 2) - The real Selenium tests in a visible browser

| # | Step | Command / action | Expected result |
|---|---|---|---|

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- Watch the same tests in a visible browser:

  ```powershell
  $env:HEADLESS='0'; pytest tests/e2e -v
  ```

- Run one journey only:

  ```powershell
  pytest tests/e2e -k journey_3 -v
  ```

- Run the whole suite (unit + integration + browser):

  ```powershell
  pytest -q
  ```

- Run one journey in a visible browser:

  ```powershell
  $env:HEADLESS='0'; pytest tests/e2e -k journey_3 -v
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| 'session not created' / Chrome version mismatch | Update Chrome, or run once with internet so Selenium Manager can fetch the matching chromedriver. In Jenkins the Dockerfile installs Chromium + chromedriver instead. |
| Tests fail with timeouts | Run one test alone to see it: `pytest tests/e2e -k journey_3 -v`. Watch it in a visible browser with `$env:HEADLESS='0'`. A failing test saves a screenshot in reports/screenshots/. |
| `pytest` is not recognised | Use `.venv\Scripts\pytest` or activate the environment. |
| Want to test a running deployment instead | `$env:E2E_BASE_URL='http://localhost:8081'; pytest tests/e2e -v` runs the same journeys against that URL. |
| Chrome does not open | Run `pytest tests/e2e -k journey_1 -v` headless first. If that works, check that no other Chrome automation is running. |
| A journey fails in the visible run | Read reports/screenshots/<test name>.png: it shows what the browser saw. Re-run that single test. |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 09 -Part code
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 09 -Part run
```
