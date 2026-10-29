# UI evidence

Real screenshots taken with headless Chrome on 2026-10-20 by
`scripts/capture_ui.py`, which starts the app on a throw-away database and
walks the full guest journey. Design notes: [../09-ui-design.md](../09-ui-design.md).

| Folder | Contents |
|---|---|
| `before/` | The original interface (desktop + mobile), captured before any change |
| `review-pass-1/` | First version of the redesign - kept to show what the visual review found |
| `after/` | Final redesign at mobile 375x812, tablet 768x1024 and desktop 1440x900, plus `docker-nginx-desktop-rooms.png` served by the Docker image through Nginx |

File names: `<size>-<step>-<page>.png`, e.g. `mobile-12-my-bookings.png`.
Steps: 01 home, 01b mobile menu open, 01c keyboard focus, 02 availability
(logged out), 03 register, 04 register error, 05 login error, 06
availability (logged in), 07 My bookings empty, 08 booking requested, 09
confirmed, 10 cancel dialog, 11 cancelled, 12 My bookings, 13 search error,
14 page not found.

## Problems found by looking at the screenshots, and fixed

| Found in | Problem | Fix |
|---|---|---|
| review-pass-1, mobile My bookings | page 396px wide in a 375px screen (measured), Cancel button overflowing | action buttons in a 2-column grid with `min-width: 0` |
| review-pass-1, mobile | footer and page titles touching the content above | CSS cascade bug: mobile `.container { padding: 0 ... }` also removed vertical padding of `.section` and the footer - changed to `padding-inline` |
| review-pass-1, register/login | arch artwork colliding with the heading | artwork moved into normal flow above the text |
| review-pass-1, availability | booked cards repeated "Not available" in empty space; tiny arches in the compact hero | removed both |
| after (first capture), search error | the date helper changed the searched check-out date on page load | only adjusts when the guest changes check-in; verified both cases |

Checks run by the script on every size: horizontal overflow (none in the
final run); cancel dialog focuses "Keep booking" and Escape closes it
without cancelling.

Regenerate: `python scripts/capture_ui.py` (needs Google Chrome).
