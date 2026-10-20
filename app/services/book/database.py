"""Relational-database Book service implementation."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.exceptions import (
    BookNotFoundError,
    DuplicateIsbnError,
    MemberNotFoundError,
)
from app.models.book import Book
from app.repositories.book import BookRepository
from app.repositories.members import MemberRepository
from app.schemas.book import BookCreate, BookUpdate
from .base import BookService


class DatabaseBookService(BookService):
    """Implement Book use cases with database persistence."""

    def __init__(self, session_factory: sessionmaker[Session]):
        # Shared session factory for creating new database sessions. Each method will create its own session to ensure thread safety and proper transaction management.
        self._session_factory = session_factory

    def list_books(self) -> list[Book]:
        """List all books in the database."""
        with self._session_factory() as session:
            return BookRepository(session).list_all()

    def get_book(self, book_id: int) -> Book:
        """Retrieve a book, raising BookNotFoundError if it does not exist."""
        with self._session_factory() as session:
            book = BookRepository(session).get_by_id(book_id)
            if book is None:
                raise BookNotFoundError(f"Book with ID {book_id} was not found")
            return book

    def create_book(self, book_create: BookCreate) -> Book:
        """Create a book after validating its member and ISBN."""
        try:
            with self._session_factory.begin() as session:
                if MemberRepository(session).get_by_id(book_create.member_id) is None:
                    raise MemberNotFoundError(
                        f"Member with ID {book_create.member_id} was not found"
                    )
                books = BookRepository(session)
                if books.get_by_isbn(book_create.isbn) is not None:
                    raise DuplicateIsbnError(
                        f"A book with ISBN {book_create.isbn} already exists"
                    )
                book = books.create(book_create)
                session.refresh(book)
                return book
        except IntegrityError:
            raise DuplicateIsbnError from None

    def replace_book(self, book_id: int, book_update: BookUpdate) -> Book:
        """Replace a book after validating its member and ISBN."""
        try:
            with self._session_factory.begin() as session:
                books = BookRepository(session)
                book = books.get_by_id(book_id)
                if book is None:
                    raise BookNotFoundError(
                        f"Book with ID {book_id} was not found"
                    )
                if MemberRepository(session).get_by_id(book_update.member_id) is None:
                    raise MemberNotFoundError(
                        f"Member with ID {book_update.member_id} was not found"
                    )
                other = books.get_by_isbn(book_update.isbn)
                if other is not None and other.id != book_id:
                    raise DuplicateIsbnError(
                        f"A book with ISBN {book_update.isbn} already exists"
                    )
                updated = books.replace(book, book_update)
                session.refresh(updated)
                return updated
        except IntegrityError:
            raise DuplicateIsbnError from None

    def delete_book(self, book_id: int) -> None:
        """Delete a book, raising BookNotFoundError if it does not exist."""
        with self._session_factory.begin() as session:
            books = BookRepository(session)
            book = books.get_by_id(book_id)
            if book is None:
                raise BookNotFoundError(f"Book with ID {book_id} was not found")
            books.delete(book)