"""SQLAlchemy model for the book table."""

from __future__ import annotations

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.members import Member

class Book(Base):
    """Map Book objects to the book table's rows in the database."""

    __tablename__ = "book"

    # Define the columns in the book table
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    isbn: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    published_year: Mapped[int] = mapped_column(nullable=False)

    # Define the relationship to the Member model
    member_id: Mapped[list[Member]] = relationship(back_populates="books")
