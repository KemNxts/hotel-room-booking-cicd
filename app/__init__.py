"""Application factory.

`create_app()` builds a fresh, fully configured Flask app. Tests call it with
their own settings (e.g. a temporary database); Gunicorn calls it via wsgi.py.
"""
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

    if not app.config["DATABASE_PATH"]:
        os.makedirs(app.instance_path, exist_ok=True)
        app.config["DATABASE_PATH"] = os.path.join(app.instance_path, "hotel.db")

    db.init_db(app.config["DATABASE_PATH"])
    app.teardown_appcontext(db.close_db)

    # Controller layer: one blueprint per area of the site.
    from .controllers import auth_routes, booking_routes, room_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(room_routes.bp)
    app.register_blueprint(booking_routes.bp)

    @app.get("/health")
    def health():
        # Used by Docker HEALTHCHECK, Jenkins and Ansible to check the app is up
        # and can reach its database.
        db.get_db().execute("SELECT 1")
        return jsonify(status="ok", env=app.config["APP_ENV"])

    @app.errorhandler(404)
    def not_found(_err):
        return render_template("404.html"), 404

    return app
