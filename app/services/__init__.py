"""Service layer: business rules. No SQL and no HTTP here.

Services receive their DAOs through the constructor (dependency injection),
so unit tests can hand them a test database or fake DAOs.
"""
from .auth_service import AuthService
from .booking_service import BookingService
from .errors import AuthError, BookingError, NotFoundError, ServiceError

__all__ = ["AuthService", "BookingService",
           "AuthError", "BookingError", "NotFoundError", "ServiceError"]
