"""PostgreSQL integration tests for SQLAlchemy repositories."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.models.book import Book
from app.models.members import Member
from app.repositories.book import BookRepository
from app.repositories.members import MemberRepository
from app.schemas.book import BookCreate
from app.schemas.members import MemberCreate


def member_data(
    *,
    name: str = "Ada Lovelace",
    email: str = "ada@example.com",
    membership_id: str = "M-001",
) -> dict[str, str]:
    return {
        "name": name,
        "email": email,
        "membership_id": membership_id,
        "phone": "(555)-123-4567",
    }


def book_data(
    *,
    isbn: str = "1234567890",
    member_id: int,
    title: str = "The Hobbit",
) -> dict[str, object]:
    return {
        "title": title,
        "author": "J. R. R. Tolkien",
        "isbn": isbn,
        "published_year": 1937,
        "member_id": member_id,
    }


def test_member_repository_persists_and_finds_members(
    database_session_factory: sessionmaker,
) -> None:
    """Verify that the member repository persists and retrieves members correctly."""
    with database_session_factory.begin() as session:
        repository = MemberRepository(session)
        first = repository.create(MemberCreate(**member_data()))
        second = repository.create(
            MemberCreate(
                **member_data(
                    name="Grace Hopper",
                    email="grace@example.com",
                    membership_id="M-002",
                )
            )
        )
        session.flush()

        assert first.id > 0
        assert repository.get_by_id(first.id) is first
        assert repository.get_by_email("ada@example.com") is first
        assert repository.get_by_membership_id("M-002") is second
        assert repository.list_all() == [first, second]


def test_book_repository_persists_and_finds_books(
    database_session_factory: sessionmaker,
) -> None:
    """Verify that the book repository persists and retrieves books correctly."""
    with database_session_factory.begin() as session:
        member = MemberRepository(session).create(MemberCreate(**member_data()))
        repository = BookRepository(session)
        first = repository.create(
            BookCreate(**book_data(member_id=member.id, isbn="0-306-40615-2"))
        )
        second = repository.create(
            BookCreate(
                **book_data(
                    member_id=member.id,
                    isbn="1234567891",
                    title="Another book",
                )
            )
        )

        assert first.id > 0
        assert repository.get_by_id(first.id) is first
        assert repository.get_by_isbn("0306406152") is first
        assert repository.list_all() == [first, second]


def test_book_repository_lists_books_for_their_member(
    database_session_factory: sessionmaker,
) -> None:
    """Verify that the book repository lists books for their member correctly."""
    with database_session_factory.begin() as session:
        members = MemberRepository(session)
        first_member = members.create(MemberCreate(**member_data()))
        second_member = members.create(
            MemberCreate(
                **member_data(
                    name="Grace Hopper",
                    email="grace@example.com",
                    membership_id="M-002",
                )
            )
        )
        books = BookRepository(session)
        first_book = books.create(
            BookCreate(**book_data(member_id=first_member.id))
        )
        books.create(
            BookCreate(
                **book_data(
                    member_id=second_member.id,
                    isbn="1234567891",
                    title="Other member book",
                )
            )
        )
        last_book = books.create(
            BookCreate(
                **book_data(
                    member_id=first_member.id,
                    isbn="1234567892",
                    title="Another book",
                )
            )
        )

        assert books.list_by_member(first_member.id) == [first_book, last_book]
        assert books.exists_for_member(first_member.id) is True
        assert books.exists_for_member(9999) is False


def test_postgres_rejects_duplicate_member_email(
    database_session_factory: sessionmaker,
) -> None:
    """Verify that the database rejects duplicate member emails."""
    with pytest.raises(IntegrityError):
        with database_session_factory.begin() as session:
            repository = MemberRepository(session)
            repository.create(MemberCreate(**member_data()))
            repository.create(
                MemberCreate(
                    **member_data(
                        name="Other member",
                        membership_id="M-002",
                    )
                )
            )


def test_postgres_rejects_duplicate_membership_id(
    database_session_factory: sessionmaker,
) -> None:
    """Verify that the database rejects duplicate membership IDs."""
    with pytest.raises(IntegrityError):
        with database_session_factory.begin() as session:
            repository = MemberRepository(session)
            repository.create(MemberCreate(**member_data()))
            repository.create(
                MemberCreate(
                    **member_data(
                        name="Other member",
                        email="other@example.com",
                    )
                )
            )


def test_postgres_rejects_duplicate_book_isbn(
    database_session_factory: sessionmaker,
) -> None:
    """Verify that the database rejects duplicate book ISBNs."""
    with pytest.raises(IntegrityError):
        with database_session_factory.begin() as session:
            member = MemberRepository(session).create(
                MemberCreate(**member_data())
            )
            repository = BookRepository(session)
            repository.create(BookCreate(**book_data(member_id=member.id)))
            repository.create(
                BookCreate(
                    **book_data(
                        member_id=member.id,
                        title="Duplicate ISBN",
                    )
                )
            )


def test_postgres_rejects_book_with_missing_member(
    database_session_factory: sessionmaker,
) -> None:
    """Verify that the database rejects a book with a non-existent member."""
    with pytest.raises(IntegrityError):
        with database_session_factory.begin() as session:
            BookRepository(session).create(
                BookCreate(**book_data(member_id=9999))
            )


def test_postgres_allows_book_with_existing_member(
    database_session_factory: sessionmaker,
) -> None:
    """Verify that the database allows a book to be created with an existing member."""
    with database_session_factory.begin() as session:
        member = MemberRepository(session).create(MemberCreate(**member_data()))
        book = BookRepository(session).create(
            BookCreate(**book_data(member_id=member.id))
        )

        assert book.member_id == member.id
        assert isinstance(book.member, Member)
        assert book.member.id == member.id
