"""Application factory.

`create_app()` builds a fresh, fully configured Flask app. Tests call it with
their own settings (e.g. a temporary database); Gunicorn calls it via wsgi.py.
"""
import logging
import os

from flask import Flask, jsonify, render_template

from . import db
from .config import DEV_SECRET_KEY, load_config


def create_app(overrides=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(load_config())
    if overrides:
        app.config.update(overrides)

    # Fail fast: outside dev/test (i.e. staging, prod) never run with a missing
    # or publicly known key, otherwise anyone could forge a login session cookie.
    if app.config["APP_ENV"] not in ("dev", "test") and \
            app.config["SECRET_KEY"] in ("", DEV_SECRET_KEY):
        raise RuntimeError(f"SECRET_KEY must be set when APP_ENV={app.config['APP_ENV']}")

    # INFO-level application events (logins, bookings) go to stderr, which
    # Gunicorn and `docker logs` show. Passwords and secrets are never logged.
    app.logger.setLevel(logging.INFO)

    if not app.config["DATABASE_PATH"]:
        os.makedirs(app.instance_path, exist_ok=True)
        app.config["DATABASE_PATH"] = os.path.join(app.instance_path, "hotel.db")

    db.init_db(app.config["DATABASE_PATH"])
    app.teardown_appcontext(db.close_db)

    # Every POST must carry the session's CSRF token (see controllers/csrf.py);
    # templates get it through the csrf_token() function.
    from .controllers.csrf import check_csrf, csrf_token
    app.before_request(check_csrf)
    app.jinja_env.globals["csrf_token"] = csrf_token

    # Controller layer: one blueprint per area of the site.
    from .controllers import auth_routes, booking_routes, room_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(room_routes.bp)
    app.register_blueprint(booking_routes.bp)

    @app.get("/health")
    def health():
        # Used by Docker HEALTHCHECK, Jenkins and Ansible to check the app is up
        # and can reach its database - and which release is running.
        db.get_db().execute("SELECT 1")
        return jsonify(status="ok", env=app.config["APP_ENV"],
                       version=app.config["APP_VERSION"], commit=app.config["GIT_COMMIT"])

    @app.errorhandler(400)
    def bad_request(err):
        return render_template("error.html", title="Request rejected",
                               message=err.description), 400

    @app.errorhandler(404)
    def not_found(_err):
        return render_template("404.html"), 404

    app.logger.info("Hotel booking app started: env=%s version=%s commit=%s",
                    app.config["APP_ENV"], app.config["APP_VERSION"], app.config["GIT_COMMIT"])
    return app
