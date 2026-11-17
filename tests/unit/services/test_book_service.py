"""Unit tests for in-memory and database Book services."""

from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import BookNotFoundError, DuplicateIsbnError, MemberNotFoundError
from app.in_memory_store import InMemoryStore
from app.models.book import Book
from app.models.members import Member
from app.schemas.book import BookCreate, BookUpdate
from app.services.book.database import DatabaseBookService
from app.services.book.in_memory import InMemoryBookService


def member_record(member_id: int = 1) -> Member:
    return Member(
        id=member_id,
        name=f"Member {member_id}",
        email=f"member{member_id}@example.com",
        membership_id=f"M-{member_id}",
        phone="(555)-123-4567",
    )


def book_payload(
    *, isbn: str = "1234567890", member_id: int = 1, title: str = "The Hobbit"
) -> dict[str, object]:
    return {
        "title": title,
        "author": "J. R. R. Tolkien",
        "isbn": isbn,
        "published_year": 1937,
        "member_id": member_id,
    }


def database_session_factory() -> tuple[MagicMock, MagicMock]:
    factory = MagicMock()
    session = MagicMock()
    factory.begin.return_value.__enter__.return_value = session
    factory.begin.return_value.__exit__.return_value = False
    factory.return_value.__enter__.return_value = session
    factory.return_value.__exit__.return_value = False
    return factory, session


def test_in_memory_book_service_creates_and_retrieves_a_book() -> None:
    """Verify that the in-memory book service can create and retrieve a book."""
    store = InMemoryStore(members=[member_record()])
    service = InMemoryBookService(store)

    created = service.create_book(BookCreate(**book_payload()))

    assert created.id == 1
    assert service.get_book(created.id) is created
    assert service.list_books() == [created]


@pytest.mark.parametrize("operation", ["create", "replace"])
def test_in_memory_book_service_rejects_a_book_for_a_missing_member(
    operation: str,
) -> None:
    """Verify that the in-memory book service rejects a book for a missing member."""
    store = InMemoryStore(
        books=[Book(id=1, **book_payload())],
        members=[member_record()],
    )
    service = InMemoryBookService(store)

    with pytest.raises(MemberNotFoundError):
        if operation == "create":
            service.create_book(BookCreate(**book_payload(member_id=4)))
        else:
            service.replace_book(1, BookUpdate(**book_payload(member_id=4)))


@pytest.mark.parametrize("operation", ["get", "replace", "delete"])
def test_in_memory_book_service_reports_missing_books(operation: str) -> None:
    """Verify that the in-memory book service reports missing books."""
    service = InMemoryBookService(InMemoryStore(members=[member_record()]))

    with pytest.raises(BookNotFoundError):
        if operation == "get":
            service.get_book(99)
        elif operation == "replace":
            service.replace_book(99, BookUpdate(**book_payload()))
        else:
            service.delete_book(99)


def test_in_memory_book_service_rejects_duplicate_normalized_isbns() -> None:
    """Verify that the in-memory book service rejects duplicate normalized ISBNs."""
    store = InMemoryStore(
        books=[Book(id=1, **book_payload(isbn="0-306-40615-2"))],
        members=[member_record()],
    )
    service = InMemoryBookService(store)

    with pytest.raises(DuplicateIsbnError):
        service.create_book(BookCreate(**book_payload(isbn="0306406152")))


def test_in_memory_book_service_allows_a_book_to_keep_its_isbn_on_replace() -> None:
    """Verify that the in-memory book service allows a book to keep its ISBN on replace."""
    original = Book(id=1, **book_payload())
    store = InMemoryStore(books=[original], members=[member_record()])
    service = InMemoryBookService(store)

    updated = service.replace_book(1, BookUpdate(**book_payload(title="Updated")))

    assert updated is original
    assert updated.title == "Updated"


def test_in_memory_book_service_replaces_and_deletes_a_book() -> None:
    """Verify that the in-memory book service can replace and delete a book."""
    original = Book(id=1, **book_payload())
    service = InMemoryBookService(
        InMemoryStore(books=[original], members=[member_record()])
    )

    service.replace_book(1, BookUpdate(**book_payload(title="Updated")))
    assert service.get_book(1).title == "Updated"

    service.delete_book(1)
    assert service.list_books() == []


def test_database_book_service_creates_when_member_exists() -> None:
    """Verify that the database book service creates a book when the member exists."""
    factory, session = database_session_factory()
    created = Book(id=7, **book_payload())

    with (
        patch("app.services.book.database.MemberRepository") as member_repository,
        patch("app.services.book.database.BookRepository") as book_repository,
    ):
        member_repository.return_value.get_by_id.return_value = member_record()
        book_repository.return_value.get_by_isbn.return_value = None
        book_repository.return_value.create.return_value = created

        result = DatabaseBookService(factory).create_book(
            BookCreate(**book_payload())
        )

    assert result is created
    book_repository.return_value.create.assert_called_once()
    session.refresh.assert_called_once_with(created)


@pytest.mark.parametrize(
    ("member_exists", "isbn_exists", "error"),
    [
        (False, False, MemberNotFoundError),
        (True, True, DuplicateIsbnError),
    ],
)
def test_database_book_service_rejects_missing_member_or_duplicate_isbn(
    member_exists: bool, isbn_exists: bool, error: type[Exception]
) -> None:
    """Verify that the database book service rejects a missing member or duplicate ISBN."""
    factory, _ = database_session_factory()

    with (
        patch("app.services.book.database.MemberRepository") as member_repository,
        patch("app.services.book.database.BookRepository") as book_repository,
    ):
        member_repository.return_value.get_by_id.return_value = (
            member_record() if member_exists else None
        )
        book_repository.return_value.get_by_isbn.return_value = (
            Book(id=2, **book_payload()) if isbn_exists else None
        )

        with pytest.raises(error):
            DatabaseBookService(factory).create_book(BookCreate(**book_payload()))


def test_database_book_service_reports_missing_book() -> None:
    """Verify that the database book service reports a missing book."""
    factory, _ = database_session_factory()

    with patch("app.services.book.database.BookRepository") as book_repository:
        book_repository.return_value.get_by_id.return_value = None
        with pytest.raises(BookNotFoundError):
            DatabaseBookService(factory).get_book(99)


def test_database_book_service_rejects_missing_replacement_member() -> None:
    """Verify that the database book service rejects a missing replacement member."""
    factory, _ = database_session_factory()
    existing_book = Book(id=1, **book_payload())

    with (
        patch("app.services.book.database.MemberRepository") as member_repository,
        patch("app.services.book.database.BookRepository") as book_repository,
    ):
        book_repository.return_value.get_by_id.return_value = existing_book
        member_repository.return_value.get_by_id.return_value = None

        with pytest.raises(MemberNotFoundError):
            DatabaseBookService(factory).replace_book(
                1, BookUpdate(**book_payload())
            )


def test_database_book_service_rejects_duplicate_isbn_from_another_book() -> None:
    """Verify that the database book service rejects a duplicate ISBN from another book."""
    factory, _ = database_session_factory()
    existing_book = Book(id=1, **book_payload())

    with (
        patch("app.services.book.database.MemberRepository") as member_repository,
        patch("app.services.book.database.BookRepository") as book_repository,
    ):
        member_repository.return_value.get_by_id.return_value = member_record()
        book_repository.return_value.get_by_id.return_value = existing_book
        book_repository.return_value.get_by_isbn.return_value = Book(
            id=2, **book_payload(isbn="1234567890")
        )

        with pytest.raises(DuplicateIsbnError):
            DatabaseBookService(factory).replace_book(
                1, BookUpdate(**book_payload())
            )


def test_database_book_service_allows_replacement_to_keep_its_isbn() -> None:
    """Verify that the database book service allows a replacement to keep its ISBN."""
    factory, session = database_session_factory()
    existing_book = Book(id=1, **book_payload())

    with (
        patch("app.services.book.database.MemberRepository") as member_repository,
        patch("app.services.book.database.BookRepository") as book_repository,
    ):
        member_repository.return_value.get_by_id.return_value = member_record()
        book_repository.return_value.get_by_id.return_value = existing_book
        book_repository.return_value.get_by_isbn.return_value = existing_book
        book_repository.return_value.replace.return_value = existing_book

        result = DatabaseBookService(factory).replace_book(
            1, BookUpdate(**book_payload(title="Updated"))
        )

    assert result is existing_book
    book_repository.return_value.replace.assert_called_once()
    session.refresh.assert_called_once_with(existing_book)


def test_database_book_service_deletes_an_existing_book() -> None:
    """Verify that the database book service can delete an existing book."""
    factory, _ = database_session_factory()
    existing_book = Book(id=1, **book_payload())

    with patch("app.services.book.database.BookRepository") as book_repository:
        book_repository.return_value.get_by_id.return_value = existing_book

        DatabaseBookService(factory).delete_book(1)

    book_repository.return_value.delete.assert_called_once_with(existing_book)
