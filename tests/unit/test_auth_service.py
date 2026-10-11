"""Feature 1: registration and login rules."""
import pytest

from app.services import AuthError


class TestRegister:
    def test_creates_user_and_stores_only_a_password_hash(self, auth_service):
        user = auth_service.register("guest@example.com", "Guest User", "password123")

        assert user.id is not None
        assert user.full_name == "Guest User"
        assert user.password_hash != "password123"
        assert "password123" not in user.password_hash

    def test_email_is_trimmed_and_lowercased(self, auth_service):
        user = auth_service.register("  Guest@Example.COM ", "Guest", "password123")
        assert user.email == "guest@example.com"

    @pytest.mark.parametrize("email", ["", "no-at-sign", "a@b", "a b@c.com"])
    def test_rejects_invalid_email(self, auth_service, email):
        with pytest.raises(AuthError, match="valid email"):
            auth_service.register(email, "Guest", "password123")

    def test_rejects_blank_name(self, auth_service):
        with pytest.raises(AuthError, match="full name"):
            auth_service.register("guest@example.com", "   ", "password123")

    def test_rejects_short_password(self, auth_service):
        with pytest.raises(AuthError, match="at least 8"):
            auth_service.register("guest@example.com", "Guest", "1234567")

    def test_rejects_duplicate_email_ignoring_case(self, auth_service, user):
        with pytest.raises(AuthError, match="already exists"):
            auth_service.register("GUEST@example.com", "Someone", "password123")


class TestLogin:
    def test_correct_credentials_return_the_user(self, auth_service, user):
        logged_in = auth_service.login("guest@example.com", "password123")
        assert logged_in.id == user.id

    def test_email_case_does_not_matter(self, auth_service, user):
        assert auth_service.login("GUEST@EXAMPLE.COM", "password123").id == user.id

    def test_wrong_password_is_rejected(self, auth_service, user):
        with pytest.raises(AuthError, match="Invalid email or password"):
            auth_service.login("guest@example.com", "wrong-password")

    def test_unknown_email_gives_the_same_message(self, auth_service):
        # Same message as a wrong password, so attackers can't discover accounts.
        with pytest.raises(AuthError, match="Invalid email or password"):
            auth_service.login("nobody@example.com", "password123")
