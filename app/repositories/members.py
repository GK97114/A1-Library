"""Database queries and persistence operations for members."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.members import Member
from app.schemas.members import MemberCreate, MemberUpdate


class MemberRepository:
    """Encapsulate SQLAlchemy operations for the Member model."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Member]:
        """Return members ordered by ID."""
        statement = select(Member).order_by(Member.id)
        return list(self._session.scalars(statement).all())

    def get_by_id(self, member_id: int) -> Member | None:
        """Find a member by its primary key."""
        return self._session.get(Member, member_id)

    def get_by_email(self, email: str) -> Member | None:
        """Find a member by email, ignoring case."""
        statement = select(Member).where(func.lower(Member.email) == email.lower())
        return self._session.scalar(statement)

    def get_by_membership_id(self, membership_id: str) -> Member | None:
        """Find a member by membership ID, ignoring case."""
        statement = select(Member).where(
            func.lower(Member.membership_id) == membership_id.lower()
        )
        return self._session.scalar(statement)

    def create(self, member_create: MemberCreate) -> Member:
        """Add a new member to the current transaction."""
        member = Member(**member_create.model_dump())
        self._session.add(member)
        self._session.flush()
        return member

    def replace(self, member: Member, member_update: MemberUpdate) -> Member:
        """Copy replacement fields onto an existing member."""
        for field, value in member_update.model_dump().items():
            setattr(member, field, value)
        self._session.flush()
        return member

    def delete(self, member: Member) -> None:
        """Mark a member for deletion in the current transaction."""
        self._session.delete(member)