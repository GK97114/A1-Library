"""Relational-database Member service implementation."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.exceptions import (
    ConflictError,
    DuplicateEmailError,
    DuplicateMembershipIdError,
    MemberHasBooksError,
    MemberNotFoundError,
)
from app.models.book import Book
from app.models.members import Member
from app.repositories.book import BookRepository
from app.repositories.members import MemberRepository
from app.schemas.members import MemberCreate, MemberUpdate
from .base import MemberService


def _ensure_unique(
    members: MemberRepository,
    email: str,
    membership_id: str,
    exclude_id: int | None = None,
) -> None:
    """Raise a duplicate error if another member uses this email or membership ID."""
    by_email = members.get_by_email(email)
    if by_email is not None and by_email.id != exclude_id:
        raise DuplicateEmailError(f"A member with email {email} already exists")
    by_membership = members.get_by_membership_id(membership_id)
    if by_membership is not None and by_membership.id != exclude_id:
        raise DuplicateMembershipIdError(
            f"A member with membership ID {membership_id} already exists"
        )


class DatabaseMemberService(MemberService):
    """Implement Member use cases with database persistence."""

    def __init__(self, session_factory: sessionmaker[Session]):
        # Each operation creates its own Session from this shared factory.
        self._session_factory = session_factory

    def list_members(self) -> list[Member]:
        with self._session_factory() as session:
            return MemberRepository(session).list_all()

    def get_member(self, member_id: int) -> Member:
        with self._session_factory() as session:
            member = MemberRepository(session).get_by_id(member_id)
            if member is None:
                raise MemberNotFoundError(f"Member with ID {member_id} was not found")
            return member

    def create_member(self, member_create: MemberCreate) -> Member:
        try:
            with self._session_factory.begin() as session:
                members = MemberRepository(session)
                _ensure_unique(
                    members, member_create.email, member_create.membership_id
                )
                member = members.create(member_create)
                session.refresh(member)
                return member
        except IntegrityError:
            # A concurrent insert slipped past the pre-check; a unique constraint caught it.
            raise ConflictError(
                "A member with this email or membership ID already exists"
            ) from None

    def replace_member(self, member_id: int, member_update: MemberUpdate) -> Member:
        try:
            with self._session_factory.begin() as session:
                members = MemberRepository(session)
                member = members.get_by_id(member_id)
                if member is None:
                    raise MemberNotFoundError(
                        f"Member with ID {member_id} was not found"
                    )
                _ensure_unique(
                    members,
                    member_update.email,
                    member_update.membership_id,
                    exclude_id=member_id,
                )
                updated = members.replace(member, member_update)
                session.refresh(updated)
                return updated
        except IntegrityError:
            raise ConflictError(
                "A member with this email or membership ID already exists"
            ) from None

    def delete_member(self, member_id: int) -> None:
        try:
            with self._session_factory.begin() as session:
                members = MemberRepository(session)
                member = members.get_by_id(member_id)
                if member is None:
                    raise MemberNotFoundError(
                        f"Member with ID {member_id} was not found"
                    )
                if BookRepository(session).exists_for_member(member_id):
                    raise MemberHasBooksError(
                        f"Member with ID {member_id} cannot be deleted because they have books"
                    )
                members.delete(member)
        except IntegrityError:
            # A book was added after the check; the foreign key blocked the delete.
            raise MemberHasBooksError(
                f"Member with ID {member_id} cannot be deleted because they have books"
            ) from None

    def list_member_books(self, member_id: int) -> list[Book]:
        with self._session_factory() as session:
            if MemberRepository(session).get_by_id(member_id) is None:
                raise MemberNotFoundError(f"Member with ID {member_id} was not found")
            return BookRepository(session).list_by_member(member_id)