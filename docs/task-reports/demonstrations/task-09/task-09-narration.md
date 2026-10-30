# Task 9 - narration script

**Task 9 - Selenium Test Design and Local Execution**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

# Part: Task 9 (part 1) - Selenium test design: the code and a real headless run

## Step 1 - Selenium and the five critical journeys [video 00:01]

**What I am doing:** running

```powershell
Select-String -Path tests/e2e/test_journeys.py -Pattern '^def test_' | ForEach-Object { $_.Line }
```

**Spoken script (as in the video):**

> This is Task 9, Selenium test design. Selenium is a tool that controls a real web browser from code: it opens pages, types in fields, clicks buttons and reads what is on the screen, like a very fast, very careful user. We chose five critical user journeys. Here are the five test functions: register, login with wrong and right password, search request and confirm, cancel and track, and a booked room being unavailable to another guest.

**What the output means:** Five test functions test_journey_1 to test_journey_5.

**What I will tell the professor:** "Five journeys cover all six workflows and the no-double-booking rule."

## Step 2 - WebDriver: the browser fixture [video 00:36]

**What I am doing:** running

```powershell
Get-Content tests/e2e/conftest.py | Select-Object -Skip 43 -First 25
```

**Spoken script (as in the video):**

> WebDriver is the standard way the test code talks to the browser. Here is the fixture that creates the browser for each test. It starts Chrome, headless by default, which means without a visible window, and that is how Jenkins runs it. Setting HEADLESS to zero shows the window. It gets the driver program from Selenium itself, and it quits the browser after every test. If a test fails, it also saves a screenshot.

**What the output means:** The driver fixture: ChromeOptions, optional headless flag, window size, chromedriver service, implicitly_wait(0), yield, then failure artifacts and quit.

**What I will tell the professor:** "Every test gets its own clean browser, started by WebDriver, and it is closed afterwards."

## Step 3 - Test data: unique and independent [video 01:10]

**What I am doing:** running

```powershell
Get-Content tests/e2e/test_journeys.py | Select-Object -Skip 14 -First 19
```

**Spoken script (as in the video):**

> Test data must not make tests depend on each other. Every test registers a new guest with a random email built from a UUID, and uses dates far in the future that change for each run. So tests never clash, even against a deployment that already has old bookings. The password is a fixed value that only exists for tests.

**What the output means:** PASSWORD constant, a random session offset, wait helper, stay() for unique dates and unique_email() with a UUID.

**What I will tell the professor:** "Each test creates its own data, so tests do not depend on each other or on old data."

## Step 4 - Element locators [video 01:36]

**What I am doing:** running

```powershell
Select-String -Path tests/e2e/test_journeys.py -Pattern '^def register' -Context 0,7 | ForEach-Object { $_.Line; $_.Context.PostContext }
```

**Spoken script (as in the video):**

> A locator tells Selenium which element on the page to use. We use ids, such as full name, email and register button. Ids are the most stable locator, because the developers put them in the page on purpose, and they do not change when the design changes. The helper function register shows the pattern: find the element, type into it, click, then wait for the result.

**What the output means:** register(): find_element(By.ID, ...) for each field, send_keys, click on register-btn, then a wait for nav-user.

**What I will tell the professor:** "Elements are found by stable ids that were added to the pages for testing."

## Step 5 - Explicit waits [video 02:06]

**What I am doing:** running

```powershell
Select-String -Path tests/e2e/*.py -Pattern 'WebDriverWait|implicitly_wait|EC\.' | Select-Object -First 8 | ForEach-Object { '{0}:{1}  {2}' -f $_.Filename, $_.LineNumber, $_.Line.Trim() }
```

**Spoken script (as in the video):**

> Web pages take time to respond, so a test must wait, but not blindly. We never use fixed sleeps. We use explicit waits: wait until this element is visible, or until this text appears, for at most ten seconds. As soon as the condition is true, the test continues. The fixture even sets the implicit wait to zero so that only our explicit waits apply. This makes tests fast and stable.

**What the output means:** Lines using WebDriverWait, implicitly_wait(0) and expected_conditions such as visibility_of_element_located.

**What I will tell the professor:** "I wait for conditions, not for fixed times, so the tests are both fast and reliable."

## Step 6 - Assertions: what the test checks [video 02:39]

**What I am doing:** running

```powershell
Select-String -Path tests/e2e/test_journeys.py -Pattern '^def test_journey_3' -Context 0,18 | ForEach-Object { $_.Line; $_.Context.PostContext }
```

**Spoken script (as in the video):**

> An assertion is the check that decides pass or fail. Here is journey three. After searching and booking, it asserts that the status is PENDING and that the dates on the page equal the dates I chose. After clicking Confirm, it waits for CONFIRMED and asserts that the message says booking confirmed, and that the confirm button is gone. If any assertion is false, the test fails and the pipeline stops.

**What the output means:** The body of journey 3 with register, search, book, assert status == 'PENDING', date checks, confirm click, wait for CONFIRMED and assertions.

**What I will tell the professor:** "Each journey asserts the visible result, so a broken feature turns the test red."

## Step 7 - Failure screenshots [video 03:09]

**What I am doing:** running

```powershell
Select-String -Path tests/e2e/conftest.py -Pattern '^def _save_failure' -Context 0,6 | ForEach-Object { $_.Line; $_.Context.PostContext }; Get-ChildItem reports/screenshots | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
```

**Spoken script (as in the video):**

> When a browser test fails, text alone is hard to understand, so the fixture saves a screenshot and the page source. This is the function. These files are real ones from earlier deliberate failure experiments, with their dates. In Jenkins they are archived with the build. A passing run creates none.

**What the output means:** The _save_failure_artifacts function (save_screenshot + page_source) and the earlier failure png/html files with their timestamps.

**What I will tell the professor:** "On a failure the pipeline keeps a picture of what the browser saw."

## Step 8 - Running the browser tests and reading the report [video 03:35]

**What I am doing:** running

```powershell
pytest -m e2e -v --junitxml=reports/e2e-demo.xml; ([xml](Get-Content reports/e2e-demo.xml)).testsuites.testsuite | Select-Object name, tests, failures, errors, skipped, time | Format-List
```

**Spoken script (as in the video):**

> Now I run the browser tests with the documented command. Pytest starts the real application on a free port, drives headless Chrome through the five journeys, and prints one line per test. I also ask for a JUnit XML report, the format Jenkins reads, and then print its summary: tests, failures and errors. The next video part shows the same tests in a visible browser.

**What the output means:** Five PASSED lines, '5 passed', then the XML summary with tests=5, failures=0, errors=0.

**What I will tell the professor:** "The five journeys pass in a real browser and produce a report that Jenkins can read."

## Step 9 - How Selenium tests differ from unit and integration tests [video 04:12]

**What I am doing:** running

```powershell
foreach ($d in 'unit','integration','e2e') { '{0,-12} {1}' -f $d, (pytest tests/$d --collect-only -q | Select-Object -Last 1) }
```

**Spoken script (as in the video):**

> How do the three kinds of test differ? Unit tests check one function or class, in isolation, in milliseconds. Integration tests send requests to the Flask app without a browser and check routes together with the database. Selenium tests use a real browser through the whole stack, so they are slowest, but they prove that a real user can complete a journey. Here are the real counts of each kind in this project.

**What the output means:** unit: 59 tests, integration: 26 tests, e2e: 5 tests collected.

**What I will tell the professor:** "Many fast unit tests at the bottom, fewer integration tests, and a few slow browser journeys on top."

# Part: Task 9 (part 2) - The real Selenium tests in a visible browser

## Step 10 - The same tests, now in a visible browser [video 04:46]

**Spoken script (as in the video):**

> This is part two. These are the real Selenium tests from the project, unchanged, now running in a visible Chrome window. I only added a short pause after every click and a red outline on the element about to be clicked, so you can follow. Without those pauses, all five journeys take about twenty seconds. Each test starts from a new guest and a clean session.

**What the output means:** A blank Chrome window with the caption; then journey 1 starts.

**What I will tell the professor:** "These are the actual automated tests; they are only slowed down for the video."

## Step 11 - Journey 1: register a new guest [video 05:13]

**Spoken script (as in the video):**

> Journey one. The test opens the register page, types a name, a unique email and a password, clicks Create account, then waits until the name appears in the navigation bar. It asserts that the name is right, that the message says the account has been created, and that the browser is on the rooms page.

**What the output means:** The register form is filled and submitted; the rooms page appears with a green message and the guest's name.

**What I will tell the professor:** "Journey 1 checks that a guest can register and is logged in."

## Step 12 - Journey 2: wrong password, then the right one [video 05:36]

**Spoken script (as in the video):**

> Journey two. The test registers a guest and logs out. Then it tries to log in with a wrong password and asserts that the error message appears and that the guest is still logged out. Then it logs in with the right password and asserts that the welcome back message appears. This checks both the refusal and the success.

**What the output means:** Error message first, then the welcome back message.

**What I will tell the professor:** "Journey 2 proves that bad credentials are refused and good ones accepted."

## Step 13 - Journey 3: search, request and confirm a booking [video 05:59]

**Spoken script (as in the video):**

> Journey three, the core of the application. A new guest searches rooms for two nights, books the first free room, and the test asserts the status is PENDING and the dates are correct. Then it clicks Confirm and waits for the status to change to CONFIRMED. It also asserts that the confirm button disappears, so a booking cannot be confirmed twice.

**What the output means:** Availability table, booking page with PENDING, then CONFIRMED.

**What I will tell the professor:** "Journey 3 covers availability, booking request and confirmation."

## Step 14 - Journey 4: cancel a booking and track the status [video 06:24]

**Spoken script (as in the video):**

> Journey four. A guest books and confirms, then clicks Cancel. A dialog asks for confirmation, and the test asserts that nothing is cancelled yet. After accepting, the status becomes CANCELLED and the cancel button disappears. Finally the test opens My bookings and asserts that the row for this booking shows CANCELLED. That is status tracking.

**What the output means:** The cancellation dialog, then CANCELLED on the booking page and in My bookings.

**What I will tell the professor:** "Journey 4 covers cancellation and status tracking."

## Step 15 - Journey 5: a booked room is unavailable to another guest [video 06:51]

**Spoken script (as in the video):**

> Journey five protects the most important rule. The first guest books a room and logs out. A second guest registers and searches the same dates. The test asserts that the room now shows Booked, and that there is no Book button for it. So two guests can never hold the same room for the same nights.

**What the output means:** The second guest's availability table shows the room as Booked.

**What I will tell the professor:** "Journey 5 proves the no double booking rule through the browser."

## Step 16 - All five journeys passed [video 07:14]

**Spoken script (as in the video):**

> That was all five journeys, with the real application and a real browser. The run ends with five passed, as in the terminal part of this video. This is what Jenkins runs in its Selenium stage, headless, every time someone pushes a commit, and a failure there stops the deployment.

**What the output means:** The browser stays on a blank page; the run is finished.

**What I will tell the professor:** "The same tests run automatically in Jenkins and block deployment if any journey fails."
