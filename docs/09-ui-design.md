# 9. User Interface Design

The portal was redesigned from a plain blue CRUD layout into a hotel
reservation site. Only templates, CSS and JavaScript changed, plus three
display-only template filters. Routes, form fields, CSRF, sessions,
business rules, the database and the DevOps setup are unchanged.

Before/after screenshots: [ui-evidence/](ui-evidence/README.md).

## Design idea

The signature element is the **door plate**: every room is shown as an arched
brass plaque with its real room number, like the plate on a hotel room door.
The arch repeats in the logo, the hero's row of arched windows (one lit),
the room chips in "My bookings" and the empty/error states. Everything around
it is kept quiet: navy, ivory, white surfaces, one accent colour.

## Design tokens (`app/static/style.css`, section 2)

| Token | Value | Use |
|---|---|---|
| `--navy-800` | `#13203B` | primary: header, hero, primary buttons, headings |
| `--navy-900` | `#0F1A31` | footer |
| `--ivory` | `#F7F5F0` | page background |
| `--surface` | `#FFFFFF` | cards, forms |
| `--brass-500` | `#A9875A` | accent: plates, rules, Register button - never small text |
| `--brass-700` | `#7E6235` | accent text (stay totals) |
| `--ink` / `--ink-muted` | `#1E2533` / `#586072` | body / secondary text |
| status colours | green / amber / red pairs | CONFIRMED + Available / PENDING / CANCELLED + Booked |

Type: **Marcellus** (headings, room numbers) - an inscriptional serif that
recalls engraved hotel signage; **Source Sans 3** (everything else). Both
are self-hosted in `app/static/fonts/` under the SIL Open Font License
(licence files next to them), so nothing is loaded from the internet.

Spacing uses a 4px-based scale (`--space-1` ... `--space-8`); radii `6/10/16px`.

## Pages

| Page | What changed |
|---|---|
| Layout (`base.html`) | Navy header with arch logo, active-page underline, account area, mobile menu; dismissible messages with icons; 3-column footer with the existing contact details; skip link |
| Rooms (`rooms.html`) | Hero with headline and "from ₹2,500 a night" (computed from the real prices); search card; rooms as door-plate cards; after a search: readable dates, nights, "4 of 6 rooms available", price per night **and** total for the stay, Available/Booked badge, "Book room 201" |
| Register / Log in | Two-column layout (navy panel + form card); field hints; inline field errors linked with `aria-describedby`; Show/Hide password |
| Booking detail | Breadcrumb; two-step progress (Requested -> Confirmed); a status panel that matches the real status; summary with readable dates and the total; room plate; cancel asks for confirmation |
| My bookings | Table on wide screens, a card per booking on phones; status badges; View and Cancel (when allowed) per booking; empty state with "Find a room" |
| 404 / errors | Same state component with a clear message and a next action |

## JavaScript (`app/static/app.js`) - progressive enhancement only

Every form still works without JavaScript, and the server validates everything.

1. Mobile menu (`aria-expanded`, Escape closes it)
2. Dismiss buttons on messages
3. Show/hide password (`aria-pressed`)
4. Date range: no past check-in, check-out minimum = check-in + 1; values
   from a search are never changed on load
5. Inline field validation messages
6. Confirmation dialog (`<dialog>`) for cancelling - focus starts on
   "Keep booking", Escape closes it without cancelling

## Accessibility

- Semantic landmarks, labelled forms, `aria-current` for the active page,
  table caption and `scope`, visually-hidden context ("Room 201, Double").
- Visible focus ring everywhere (light brass on dark areas).
- Status is never colour-only: the badge text is the status, and the
  cancelled badge has a different marker shape.
- Contrast (WCAG 2.1, computed): all text pairs >= 4.5:1, e.g. body 14.1:1,
  muted 5.8:1, badges 5.5-6.0:1, brass totals 5.7:1.
- `prefers-reduced-motion` respected (only small hover transitions exist).

## Responsive

Breakpoints at 960px (single-column booking page and auth), 860px (mobile menu,
booking cards) and 520px (single-column search). Checked by
`scripts/capture_ui.py` at 375x812, 768x1024 and 1440x900 - it measures
horizontal overflow on every page.

## Backend change (minimal)

`app/__init__.py` registers three display-only Jinja filters: `to_date`
(ISO string -> date), `long_date` (-> "Thu 10 Jan 2030") and `money`
(2500 -> "₹2,500"). No business logic.

## Test contract changes

Four assertions changed because the UI genuinely changed; none were weakened:

| Test | Before | After |
|---|---|---|
| `test_home_redirects_to_rooms_and_lists_six_rooms` | counted 6 `<tr><td>` | counts 6 room cards **and** checks all six room numbers |
| `test_availability_search_shows_booked_room` | regex on `<tr id="room-101">` | regex on the card; also checks the Book button is absent/present |
| e2e journey 3 | date text == ISO | `datetime` attribute == ISO **and** text == readable date |
| e2e journey 4 | click Cancel | click Cancel -> dialog opens, status still CONFIRMED -> confirm -> CANCELLED |
