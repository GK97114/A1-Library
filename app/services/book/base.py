"""Abstract interface for book services."""

from abc import ABC, abstractmethod

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


class BookService(ABC):
    """Define the operations supported by each book service implementation."""

    @abstractmethod
    def create_book(self, book_create: BookCreate) -> Book:
        """Create and return a book."""

    @abstractmethod
    def get_book(self, book_id: int) -> Book:
        """Return a book, or raise BookNotFoundError if it does not exist."""

    @abstractmethod
    def replace_book(self, book_id: int, book_update: BookUpdate) -> Book:
        """Replace a book, or raise a domain error if it cannot be replaced."""

    @abstractmethod
    def delete_book(self, book_id: int) -> None:
        """Delete a book, or raise BookNotFoundError if it does not exist."""

    @abstractmethod
    def list_books(self) -> list[Book]:
        """Return all books."""
