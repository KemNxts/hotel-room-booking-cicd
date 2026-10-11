class ServiceError(Exception):
    """A business-rule failure with a message that is safe to show the user."""


class AuthError(ServiceError):
    pass


class BookingError(ServiceError):
    pass


class NotFoundError(ServiceError):
    pass
