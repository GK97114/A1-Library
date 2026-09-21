"""Temporary in-memory storage shared by all routers."""

from app.schemas.book import BookResponse
from app.schemas.members import MemberResponse


books: list[BookResponse] = [
    BookResponse(
        title="1984",
        BookAuthor="George Orwell",
        Bookisbn="978-0451524935",
        published_year=1949,
        member_id=None,
        id=1
    )
]

members: list[MemberResponse] = [
    MemberResponse(
        name="John Doe",
        email="john.doe@example.com",
        memberships_id="CCCCL-0001",
        phone="(555)-123-4567",
        id=1
    )
]