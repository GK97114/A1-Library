"""FastAPI dependencies that expose application services to to HTTP routes in the API Layer."""

from fastapi import Request

from app.services.book import BookService
from app.services.members import MemberService

