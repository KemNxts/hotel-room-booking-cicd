"""Entry point.

Production:  gunicorn --bind 0.0.0.0:8000 wsgi:app
Development: python wsgi.py   (Flask's built-in server, auto-reload)
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config["APP_ENV"] == "dev")
