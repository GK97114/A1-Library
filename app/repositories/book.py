"""Database queries and persistence operations for books."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


class BookRepository:
    """Encapsulate SQLAlchemy operations for the Book model."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Book]:
        """Return books ordered by ID."""
        statement = select(Book).order_by(Book.id)
        return list(self._session.scalars(statement).all())

    def get_by_id(self, book_id: int) -> Book | None:
        """Find a book by its primary key."""
        return self._session.get(Book, book_id)

    def get_by_isbn(self, isbn: str) -> Book | None:
        """Find a book by ISBN, ignoring spaces and hyphens."""
        normalized_isbn = isbn.replace("-", "").replace(" ", "").upper()
        normalized_column = func.upper(
            func.replace(func.replace(Book.isbn, "-", ""), " ", "")
        )
        statement = select(Book).where(normalized_column == normalized_isbn)
        return self._session.scalar(statement)

    def create(self, book_create: BookCreate) -> Book:
        """Add a new book to the current transaction."""
        book = Book(**book_create.model_dump())
        self._session.add(book)
        self._session.flush()
        return book

    def replace(self, book: Book, book_update: BookUpdate) -> Book:
        """Copy replacement fields onto an existing book."""
        for field, value in book_update.model_dump().items():
            setattr(book, field, value)
        self._session.flush()
        return book

    def delete(self, book: Book) -> None:
        """Mark a book for deletion in the current transaction."""
        self._session.delete(book)