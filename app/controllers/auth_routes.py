"""Feature 1: registration, login, logout."""
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from app.services import AuthError

from .helpers import auth_service, safe_next_url

bp = Blueprint("auth", __name__)


@bp.before_app_request
def load_logged_in_user():
    """Runs before every request: put the current user (or None) on `g`."""
    user_id = session.get("user_id")
    g.user = auth_service().get_user(user_id) if user_id else None


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            user = auth_service().register(
                request.form.get("email"),
                request.form.get("full_name"),
                request.form.get("password"),
            )
        except AuthError as err:
            flash(str(err), "error")
            return render_template("register.html", form=request.form), 400
        _start_session(user)
        flash(f"Welcome, {user.full_name}! Your account has been created.", "success")
        return redirect(url_for("rooms.list_rooms"))
    return render_template("register.html", form={})


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            user = auth_service().login(request.form.get("email"), request.form.get("password"))
        except AuthError as err:
            flash(str(err), "error")
            return render_template("login.html", form=request.form), 401
        _start_session(user)
        flash(f"Welcome back, {user.full_name}.", "success")
        return redirect(safe_next_url(request.args.get("next")))
    return render_template("login.html", form={})


@bp.post("/logout")  # POST, not GET, so a link/image elsewhere can't log you out
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


def _start_session(user):
    # Clear first so no data from a previous session survives the login.
    session.clear()
    session["user_id"] = user.id
