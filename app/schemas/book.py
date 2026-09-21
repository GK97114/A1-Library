from datetime import date
from pydantic import BaseModel, ConfigDict, Field

current_year = date.today().year

class BookBase(BaseModel):
    """Define fields shared by all Book schemas"""
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(
        required=True,
        min_length=1,
        max_length=200
    )

    BookAuthor: str = Field(
        required=True,
        min_length=1,
        max_length=120
    )

    Bookisbn: str = Field(
        required=True,
        min_length=10,
        max_length=17
    )

    published_year: int = Field(
        ge=1450,
        le=current_year
    )

    member_id: int | None = Field(
        required=True,
        default=None,
        description="The ID of the member who has borrowed the book, if any"
    )

class BookCreate(BookBase):
    """Validate the body used to create a new book"""

class BookUpdate(BookBase):
    """Validate the replacement body used to update an existing book"""

class BookResponse(BookBase):
    """Describe a book returned by the API."""

    id: int = Field(
        gt=0,
        description="The unique identifier for the book",
        examples=[1],   # Provide an example of a valid book ID
    )