"""Unit tests for in-memory and database Member services."""

from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import (
    DuplicateEmailError,
    DuplicateMembershipIdError,
    MemberHasBooksError,
    MemberNotFoundError,
)
from app.in_memory_store import InMemoryStore
from app.models.book import Book
from app.models.members import Member
from app.schemas.members import MemberCreate, MemberUpdate
from app.services.members.database import DatabaseMemberService
from app.services.members.in_memory import InMemoryMemberService


def member_payload(
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


def member_record(
    member_id: int = 1,
    *,
    email: str | None = None,
    membership_id: str | None = None,
) -> Member:
    return Member(
        id=member_id,
        name=f"Member {member_id}",
        email=email or f"member{member_id}@example.com",
        membership_id=membership_id or f"M-{member_id}",
        phone="(555)-123-4567",
    )


def book_record(book_id: int, member_id: int) -> Book:
    return Book(
        id=book_id,
        title=f"Book {book_id}",
        author="Author",
        isbn=f"{book_id:010d}",
        published_year=2020,
        member_id=member_id,
    )


def database_session_factory() -> tuple[MagicMock, MagicMock]:
    factory = MagicMock()
    session = MagicMock()
    factory.begin.return_value.__enter__.return_value = session
    factory.begin.return_value.__exit__.return_value = False
    factory.return_value.__enter__.return_value = session
    factory.return_value.__exit__.return_value = False
    return factory, session


def test_in_memory_member_service_creates_and_retrieves_a_member() -> None:
    service = InMemoryMemberService(InMemoryStore())

    created = service.create_member(MemberCreate(**member_payload()))

    assert created.id == 1
    assert service.get_member(created.id) is created
    assert service.list_members() == [created]


@pytest.mark.parametrize("operation", ["get", "replace", "delete", "list_books"])
def test_in_memory_member_service_reports_a_missing_member(operation: str) -> None:
    service = InMemoryMemberService(InMemoryStore())

    with pytest.raises(MemberNotFoundError):
        if operation == "get":
            service.get_member(99)
        elif operation == "replace":
            service.replace_member(99, MemberUpdate(**member_payload()))
        elif operation == "delete":
            service.delete_member(99)
        else:
            service.list_member_books(99)


def test_in_memory_member_service_lists_only_the_members_books() -> None:
    store = InMemoryStore(
        members=[member_record(1), member_record(2)],
        books=[book_record(1, 1), book_record(2, 2), book_record(3, 1)],
    )

    books = InMemoryMemberService(store).list_member_books(1)

    assert [book.id for book in books] == [1, 3]


def test_in_memory_member_service_blocks_deletion_when_books_exist() -> None:
    member = member_record()
    store = InMemoryStore(members=[member], books=[book_record(1, member.id)])

    with pytest.raises(MemberHasBooksError):
        InMemoryMemberService(store).delete_member(member.id)

    assert store.members == [member]


def test_in_memory_member_service_deletes_a_member_without_books() -> None:
    member = member_record()
    store = InMemoryStore(members=[member])

    InMemoryMemberService(store).delete_member(member.id)

    assert store.members == []


@pytest.mark.parametrize(
    ("duplicate_payload", "error"),
    [
        (member_payload(email="ADA@example.com"), DuplicateEmailError),
        (
            member_payload(email="other@example.com", membership_id="m-001"),
            DuplicateMembershipIdError,
        ),
    ],
)
def test_in_memory_member_service_rejects_duplicate_email_or_membership_id(
    duplicate_payload: dict[str, str], error: type[Exception]
) -> None:
    store = InMemoryStore(
        members=[member_record(email="ada@example.com", membership_id="M-001")]
    )

    with pytest.raises(error):
        InMemoryMemberService(store).create_member(
            MemberCreate(**duplicate_payload)
        )


def test_database_member_service_creates_when_identifiers_are_unique() -> None:
    factory, session = database_session_factory()
    created = member_record(7)

    with patch(
        "app.services.members.database.MemberRepository"
    ) as member_repository:
        repository = member_repository.return_value
        repository.get_by_email.return_value = None
        repository.get_by_membership_id.return_value = None
        repository.create.return_value = created

        result = DatabaseMemberService(factory).create_member(
            MemberCreate(**member_payload())
        )

    assert result is created
    repository.create.assert_called_once()
    session.refresh.assert_called_once_with(created)


@pytest.mark.parametrize(
    ("duplicate_kind", "error"),
    [
        ("email", DuplicateEmailError),
        ("membership_id", DuplicateMembershipIdError),
    ],
)
def test_database_member_service_rejects_duplicate_email_or_membership_id(
    duplicate_kind: str, error: type[Exception]
) -> None:
    factory, _ = database_session_factory()

    with patch(
        "app.services.members.database.MemberRepository"
    ) as member_repository:
        repository = member_repository.return_value
        repository.get_by_email.return_value = (
            member_record(2, email="ada@example.com")
            if duplicate_kind == "email"
            else None
        )
        repository.get_by_membership_id.return_value = (
            member_record(3, membership_id="M-001")
            if duplicate_kind == "membership_id"
            else None
        )

        with pytest.raises(error):
            DatabaseMemberService(factory).create_member(
                MemberCreate(**member_payload())
            )


@pytest.mark.parametrize("operation", ["get", "replace", "delete"])
def test_database_member_service_reports_a_missing_member(operation: str) -> None:
    factory, _ = database_session_factory()

    with (
        patch(
            "app.services.members.database.MemberRepository"
        ) as member_repository,
        patch("app.services.members.database.BookRepository"),
    ):
        member_repository.return_value.get_by_id.return_value = None
        service = DatabaseMemberService(factory)

        with pytest.raises(MemberNotFoundError):
            if operation == "get":
                service.get_member(99)
            elif operation == "replace":
                service.replace_member(99, MemberUpdate(**member_payload()))
            else:
                service.delete_member(99)


def test_database_member_service_lists_only_the_members_books() -> None:
    factory, _ = database_session_factory()
    expected_books = [book_record(1, 1)]

    with (
        patch(
            "app.services.members.database.MemberRepository"
        ) as member_repository,
        patch(
            "app.services.members.database.BookRepository"
        ) as book_repository,
    ):
        member_repository.return_value.get_by_id.return_value = member_record()
        book_repository.return_value.list_by_member.return_value = expected_books

        result = DatabaseMemberService(factory).list_member_books(1)

    assert result == expected_books
    book_repository.return_value.list_by_member.assert_called_once_with(1)


def test_database_member_service_blocks_deletion_when_books_exist() -> None:
    factory, _ = database_session_factory()

    with (
        patch(
            "app.services.members.database.MemberRepository"
        ) as member_repository,
        patch(
            "app.services.members.database.BookRepository"
        ) as book_repository,
    ):
        member = member_record()
        member_repository.return_value.get_by_id.return_value = member
        book_repository.return_value.exists_for_member.return_value = True

        with pytest.raises(MemberHasBooksError):
            DatabaseMemberService(factory).delete_member(member.id)

        member_repository.return_value.delete.assert_not_called()


def test_database_member_service_deletes_a_member_without_books() -> None:
    factory, _ = database_session_factory()

    with (
        patch(
            "app.services.members.database.MemberRepository"
        ) as member_repository,
        patch(
            "app.services.members.database.BookRepository"
        ) as book_repository,
    ):
        member = member_record()
        member_repository.return_value.get_by_id.return_value = member
        book_repository.return_value.exists_for_member.return_value = False

        DatabaseMemberService(factory).delete_member(member.id)

    member_repository.return_value.delete.assert_called_once_with(member)
