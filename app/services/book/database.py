"""Relational database models for the Book service implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
from app.services.book.base import BookService

class BookService(BookService):
    """Define book use cases for the relational database implementation."""
    