"""SQLAlchemy model for the members table."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.book import Book

class Member(Base):
    """Map Member objects to the members table's rows in the database."""

    __tablename__ = "members"

    # Define the columns in the members table
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    membership_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)

    # Define the relationship to the Book model
    books: Mapped[list[Book]] = relationship(back_populates="member_id")