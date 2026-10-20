"""In-memory implementation of the book service."""

from app.exceptions import (
    BookNotFoundError,
    DuplicateIsbnError,
    MemberNotFoundError,
)
from app.in_memory_store import InMemoryStore
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
from .base import BookService

def normalize_isbn(isbn: str) -> str:
    """Normalize common ISBN formatting before checking for duplicates."""
    return isbn.replace("-", "").replace(" ", "").upper()


class InMemoryBookService(BookService):
    """Implement book operations using a shared in-memory store."""

    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def list_books(self) -> list[Book]:
        """Return a snapshot of all books in the store."""
        with self._store.lock:
            return list(self._store.books)

    def get_book(self, book_id: int) -> Book:
        """Return a book, raising BookNotFoundError if it does not exist."""
        with self._store.lock:
            for book in self._store.books:
                if book.id == book_id:
                    return book
        raise BookNotFoundError(f"Book with ID {book_id} was not found")

    def create_book(self, book_create: BookCreate) -> Book:
        """Create a book after validating its member and ISBN."""
        with self._store.lock:
            if not any(member.id == book_create.member_id for member in self._store.members):
                raise MemberNotFoundError(
                    f"Member with ID {book_create.member_id} was not found"
                )
            normalized_isbn = normalize_isbn(book_create.isbn)
            if any(
                normalize_isbn(book.isbn) == normalized_isbn
                for book in self._store.books
            ):
                raise DuplicateIsbnError(
                    f"A book with ISBN {book_create.isbn} already exists"
                )

            next_id = max((book.id for book in self._store.books), default=0) + 1
            book = Book(id=next_id, **book_create.model_dump())
            self._store.books.append(book)
            return book

    def replace_book(self, book_id: int, book_update: BookUpdate) -> Book:
        """Replace a book after validating its member and ISBN."""
        with self._store.lock:
            book = next(
                (book for book in self._store.books if book.id == book_id),
                None,
            )
            if book is None:
                raise BookNotFoundError(f"Book with ID {book_id} was not found")
            if not any(member.id == book_update.member_id for member in self._store.members):
                raise MemberNotFoundError(
                    f"Member with ID {book_update.member_id} was not found"
                )

            normalized_isbn = normalize_isbn(book_update.isbn)
            if any(
                existing.id != book_id
                and normalize_isbn(existing.isbn) == normalized_isbn
                for existing in self._store.books
            ):
                raise DuplicateIsbnError(
                    f"A book with ISBN {book_update.isbn} already exists"
                )

            for field, value in book_update.model_dump().items():
                setattr(book, field, value)
            return book

    def delete_book(self, book_id: int) -> None:
        """Delete a book, raising BookNotFoundError if it does not exist."""
        with self._store.lock:
            for index, book in enumerate(self._store.books):
                if book.id == book_id:
                    del self._store.books[index]
                    return
        raise BookNotFoundError(f"Book with ID {book_id} was not found")
