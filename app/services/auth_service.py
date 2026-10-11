import re
import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from .errors import AuthError

# Deliberately simple: something@something.something
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


class AuthService:
    def __init__(self, user_dao):
        self.users = user_dao

    def register(self, email, full_name, password):
        """Create an account and return the new User."""
        email = (email or "").strip().lower()
        full_name = (full_name or "").strip()
        password = password or ""

        if not EMAIL_RE.match(email):
            raise AuthError("Please enter a valid email address.")
        if not full_name:
            raise AuthError("Please enter your full name.")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise AuthError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        if self.users.find_by_email(email):
            raise AuthError("An account with this email already exists.")

        # Never store the plain password - only a salted hash (Werkzeug's
        # default is scrypt). The same password gives a different hash each time.
        try:
            user_id = self.users.create(email, full_name, generate_password_hash(password))
        except sqlite3.IntegrityError:
            # Two sign-ups with the same email at the same moment.
            raise AuthError("An account with this email already exists.") from None
        return self.users.find_by_id(user_id)

    def login(self, email, password):
        """Return the User if the credentials are correct, else raise AuthError."""
        user = self.users.find_by_email((email or "").strip().lower())
        # Same message for "no such user" and "wrong password" so an attacker
        # cannot find out which emails are registered.
        if user is None or not check_password_hash(user.password_hash, password or ""):
            raise AuthError("Invalid email or password.")
        return user

    def get_user(self, user_id):
        return self.users.find_by_id(user_id)
