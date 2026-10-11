"""CSRF protection (Cross-Site Request Forgery).

Without it, a malicious page could make a logged-in guest's browser submit
"cancel booking 12" to our site, and the browser would attach the session
cookie automatically. To prevent that, every form we render carries a random
token that is also stored in the user's session. A POST is accepted only if
the two match - another site cannot read our pages, so it cannot know the token.
"""
import hmac
import secrets

from flask import abort, current_app, request, session

SESSION_KEY = "_csrf"
FORM_FIELD = "csrf_token"


def csrf_token():
    """Return this session's token, creating it on first use (used in templates)."""
    if SESSION_KEY not in session:
        session[SESSION_KEY] = secrets.token_hex(32)
    return session[SESSION_KEY]


def check_csrf():
    """before_request hook: reject state-changing requests without a valid token."""
    if request.method != "POST":
        return
    expected = session.get(SESSION_KEY)
    sent = request.form.get(FORM_FIELD, "")
    # compare_digest takes the same time whatever the input, so the token
    # cannot be guessed character by character from response times.
    if not expected or not hmac.compare_digest(expected, sent):
        current_app.logger.warning("Rejected POST %s: missing or invalid CSRF token", request.path)
        abort(400, description="Your form has expired or is invalid. Please go back, reload the page and try again.")
