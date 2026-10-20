"""Abstract interface for member services."""

from abc import ABC, abstractmethod

from app.models.book import Book
from app.models.members import Member
from app.schemas.members import MemberCreate, MemberUpdate


class MemberService(ABC):
    """Define the operations supported by each member service implementation."""

    @abstractmethod
    def list_members(self) -> list[Member]:
        """Return all members."""

    @abstractmethod
    def get_member(self, member_id: int) -> Member:
        """Return a member, or raise MemberNotFoundError if it does not exist."""

    @abstractmethod
    def create_member(self, member_create: MemberCreate) -> Member:
        """Create and return a member, or raise a duplicate error."""

    @abstractmethod
    def replace_member(self, member_id: int, member_update: MemberUpdate) -> Member:
        """Replace a member, or raise MemberNotFoundError or a duplicate error."""

    @abstractmethod
    def delete_member(self, member_id: int) -> None:
        """Delete a member, or raise MemberNotFoundError or MemberHasBooksError."""

    @abstractmethod
    def list_member_books(self, member_id: int) -> list[Book]:
        """Return the books associated with a member, or raise MemberNotFoundError."""