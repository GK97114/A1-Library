"""Database queries for members used by other repositories and services."""

from sqlalchemy.orm import Session

from app.models.members import Member


class MemberRepository:
    """Encapsulate SQLAlchemy queries for the Member model."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, member_id: int) -> Member | None:
        """Find a member by its primary key."""
        return self._session.get(Member, member_id)