"""SQLAlchemy model for the book table."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.members import Member

class Book(Base):
    """Map Book objects to the book table's rows in the database."""

    __tablename__ = "book"

    # Define the columns in the book table
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    isbn: Mapped[str] = mapped_column(String(17), nullable=False, unique=True)
    published_year: Mapped[int] = mapped_column(nullable=False)

    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False)
    member: Mapped["Member"] = relationship(back_populates="books")
