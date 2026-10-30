# Task 9 - viva questions and answers

**Task 9 - Selenium Test Design and Local Execution**

Source: section G of [task-09-selenium-test-design-and-execution.md](../../task-09-selenium-test-design-and-execution.md) - answers checked against the
repository and the evidence in this project.

1. **What is Selenium WebDriver?** A library and protocol that lets code control a real browser - open pages, type, click, read text.
2. **Which journeys did you automate and why?** Register; wrong-then-right
   login; search-book-confirm; cancel and track status; a booked room is
   unavailable to another guest - the six MVP workflows end to end.
3. **What is an explicit wait?** Waiting for a condition (e.g. element
   visible) up to a timeout, continuing as soon as it is true. Better than `sleep`.
4. **Why ids as locators?** They are unique and do not change when layout or
   styling changes; the UI redesign kept them, so the tests still passed.
5. **How do you keep test data from interfering?** Each local run uses a new
   temporary database; against deployments, unique e-mails and random future dates.
6. **How do screenshots on failure work?** A pytest hook records the result;
   the browser fixture saves a PNG and the HTML if the test failed.
7. **(Project-specific) Why are dates set with JavaScript?** Typing into a
   date input depends on the OS date format; setting `value` is identical everywhere.
8. **(Project-specific) What changed in the tests for the UI redesign?**
   Journey 4 now confirms the cancel dialog; journey 3 reads the ISO date from
   the `datetime` attribute and checks the readable text. Both still assert the same behaviour.
9. **Unit vs integration vs Selenium?** Unit: one rule, no server. Integration:
   real HTTP routes in-process. Selenium: the full journey in a browser.
10. **Do you run Selenium through Maven?** No - through pytest. It produces JUnit
    XML like Maven's Surefire would. Confirm with the professor if Maven is mandatory.
11. **How does Jenkins run a browser without a screen?** Headless Chromium inside the Jenkins container (`CHROME_BIN`, `CHROMEDRIVER` set in its Dockerfile).

## Extra questions that match this demonstration

1. **Which five journeys did you choose, and why those?**
   Register; login with a wrong then right password; search, request and confirm a booking; cancel and track the status; and a booked room being unavailable to another guest. Together they cover all six MVP workflows and the most important business rule (no double booking).

2. **Are the screenshots in reports/screenshots from a failure that happened by accident?**
   They are from earlier deliberate-failure experiments (Tasks 9 and 10), kept to prove that the screenshot-on-failure feature works. A passing run does not create any.

3. **Is the browser in the video really running your test code?**
   Yes. It is tests/e2e/test_journeys.py, unchanged. The recording only adds a pause after every click and keystroke, a red outline on the element about to be clicked, and a caption at the bottom, so a viewer can follow. Without those pauses the five tests finish in about 20 seconds.
