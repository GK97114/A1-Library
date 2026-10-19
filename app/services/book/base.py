"""Abstract base class for book services."""

from abc import ABC, abstractmethod

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate

class BookServiceBase(ABC):
    """Abstract base class for book services."""

    @abstractmethod
    async def create_book(self, book_create: BookCreate) -> Book:
        """Create a new book in the database."""
        pass

    @abstractmethod
    async def get_book(self, book_id: int) -> Book | None:
        """Retrieve a book by its ID from the database."""
        pass

    @abstractmethod
    async def update_book(self, book_id: int, book_update: BookUpdate) -> Book | None:
        """Update an existing book in the database."""
        pass

    @abstractmethod
    async def delete_book(self, book_id: int) -> bool:
        """Delete a book from the database."""
        pass

    @abstractmethod
    async def list_books(self) -> list[Book]:
        """List all books in the database."""
        pass