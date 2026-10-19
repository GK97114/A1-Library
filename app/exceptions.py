class BookNotFoundError(Exception):
    """Raised when a book is not found in the database."""

class DuplicateIsbnError(Exception):
    """Raised when a book with the same ISBN already exists in the database."""
    
class MemberNotFoundError(Exception):
    """Raised when a member is not found in the database."""
