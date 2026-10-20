"""Domain errors raised by services. Routers never see database details."""


class NotFoundError(Exception):
    """Base class for missing-resource errors (HTTP 404)."""


class ConflictError(Exception):
    """Base class for conflict errors (HTTP 409)."""


class BookNotFoundError(NotFoundError):
    """Raised when a book does not exist."""


class MemberNotFoundError(NotFoundError):
    """Raised when a member does not exist."""


class DuplicateIsbnError(ConflictError):
    """Raised when another book already uses this ISBN."""


class DuplicateEmailError(ConflictError):
    """Raised when another member already uses this email."""


class DuplicateMembershipIdError(ConflictError):
    """Raised when another member already uses this membership ID."""


class MemberHasBooksError(ConflictError):
    """Raised when deleting a member who still has books."""