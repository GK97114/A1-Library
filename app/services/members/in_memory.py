"""In-memory implementation of the member service."""

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
from .base import MemberService


class InMemoryMemberService(MemberService):
    """Implement member operations using a shared in-memory store."""

    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def _ensure_unique(
        self, email: str, membership_id: str, exclude_id: int | None = None
    ) -> None:
        """Raise a duplicate error if another member uses this email or membership ID."""
        for existing in self._store.members:
            if existing.id == exclude_id:
                continue
            if existing.email.casefold() == email.casefold():
                raise DuplicateEmailError(
                    f"A member with email {email} already exists"
                )
            if existing.membership_id.casefold() == membership_id.casefold():
                raise DuplicateMembershipIdError(
                    f"A member with membership ID {membership_id} already exists"
                )

    def list_members(self) -> list[Member]:
        """Return a snapshot of all members in the store."""
        with self._store.lock:
            return list(self._store.members)

    def get_member(self, member_id: int) -> Member:
        """Return a member, raising MemberNotFoundError if it does not exist."""
        with self._store.lock:
            for member in self._store.members:
                if member.id == member_id:
                    return member
        raise MemberNotFoundError(f"Member with ID {member_id} was not found")

    def create_member(self, member_create: MemberCreate) -> Member:
        """Create a member after checking for duplicates."""
        with self._store.lock:
            self._ensure_unique(member_create.email, member_create.membership_id)
            next_id = max((m.id for m in self._store.members), default=0) + 1
            member = Member(id=next_id, **member_create.model_dump())
            self._store.members.append(member)
            return member

    def replace_member(self, member_id: int, member_update: MemberUpdate) -> Member:
        """Replace a member after checking for duplicates."""
        with self._store.lock:
            member = self.get_member(member_id)
            self._ensure_unique(
                member_update.email, member_update.membership_id, exclude_id=member_id
            )
            for field, value in member_update.model_dump().items():
                setattr(member, field, value)
            return member

    def delete_member(self, member_id: int) -> None:
        """Delete a member who has no books."""
        with self._store.lock:
            member = self.get_member(member_id)
            if any(book.member_id == member_id for book in self._store.books):
                raise MemberHasBooksError(
                    f"Member with ID {member_id} cannot be deleted because they have books"
                )
            self._store.members.remove(member)

    def list_member_books(self, member_id: int) -> list[Book]:
        """Return the books associated with a member."""
        with self._store.lock:
            self.get_member(member_id)
            return [b for b in self._store.books if b.member_id == member_id]