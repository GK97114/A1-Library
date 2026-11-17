"""Unit tests for the Book Pydantic schemas."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse, BookUpdate


def valid_book_data() -> dict[str, object]:
    """Return a valid Book payload that tests can modify independently."""
    return {
        "title": "The Hobbit",
        "author": "J. R. R. Tolkien",
        "isbn": "1234567890",
        "published_year": 1937,
        "member_id": 1,
    }


@pytest.mark.parametrize(
    "field",
    ["title", "author", "isbn", "published_year", "member_id"],
)
def test_book_create_requires_each_application_field(field: str) -> None:
    """Verify that each required field is indeed required."""
    payload = valid_book_data()
    del payload[field]

    with pytest.raises(ValidationError):
        BookCreate.model_validate(payload)


def test_book_response_requires_a_positive_id() -> None:
    """Verify that the BookResponse schema requires a positive ID."""
    payload = valid_book_data()

    with pytest.raises(ValidationError):
        BookResponse.model_validate(payload)

    for book_id in (0, -1):
        with pytest.raises(ValidationError):
            BookResponse.model_validate({**payload, "id": book_id})


def test_book_response_accepts_a_sqlalchemy_book() -> None:
    """Verify that the BookResponse schema accepts a SQLAlchemy Book instance."""
    book = Book(id=1, **valid_book_data())

    response = BookResponse.model_validate(book)

    assert response.id == 1
    assert response.title == "The Hobbit"


def test_book_create_accepts_text_length_and_year_boundaries() -> None:
    """Verify that BookCreate accepts valid text lengths and published year boundaries."""
    year = date.today().year

    for title, author, isbn, published_year in (
        ("T", "A", "1" * 10, 1450),
        ("T" * 200, "A" * 120, "1" * 17, year),
    ):
        payload = {
            **valid_book_data(),
            "title": title,
            "author": author,
            "isbn": isbn,
            "published_year": published_year,
        }
        assert BookCreate.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("title", "T" * 201),
        ("author", ""),
        ("author", "A" * 121),
        ("isbn", "1" * 9),
        ("isbn", "1" * 18),
    ],
)
def test_book_create_rejects_text_lengths_outside_boundaries(
    field: str, value: str
) -> None:
    """Verify that BookCreate rejects text lengths outside the allowed boundaries."""
    with pytest.raises(ValidationError):
        BookCreate.model_validate({**valid_book_data(), field: value})


@pytest.mark.parametrize("published_year", [1449, date.today().year + 1])
def test_book_create_rejects_invalid_published_year(published_year: int) -> None:
    """Verify that BookCreate rejects published years outside the allowed range."""
    with pytest.raises(ValidationError):
        BookCreate.model_validate(
            {**valid_book_data(), "published_year": published_year}
        )


@pytest.mark.parametrize("member_id", [0, -1])
def test_book_create_rejects_nonpositive_member_id(member_id: int) -> None:
    """Verify that BookCreate rejects non-positive member IDs."""
    with pytest.raises(ValidationError):
        BookCreate.model_validate({**valid_book_data(), "member_id": member_id})


def test_book_create_trims_surrounding_whitespace() -> None:
    """Verify that BookCreate trims surrounding whitespace from text fields."""
    payload = {
        **valid_book_data(),
        "title": "  The Hobbit  ",
        "author": "  J. R. R. Tolkien ",
        "isbn": " 1234567890 ",
    }

    book = BookCreate.model_validate(payload)

    assert book.title == "The Hobbit"
    assert book.author == "J. R. R. Tolkien"
    assert book.isbn == "1234567890"


@pytest.mark.parametrize("field", ["title", "author", "isbn"])
def test_book_create_rejects_whitespace_only_required_text(field: str) -> None:
    """Verify that BookCreate rejects required text fields that are only whitespace."""
    with pytest.raises(ValidationError):
        BookCreate.model_validate({**valid_book_data(), field: "   "})


def test_book_create_rejects_unknown_fields() -> None:
    """Verify that BookCreate rejects unknown fields."""
    with pytest.raises(ValidationError):
        BookCreate.model_validate({**valid_book_data(), "unknown": "value"})


def test_book_update_applies_the_same_book_field_rules() -> None:
    """Verify that BookUpdate applies the same field validation rules as BookCreate."""
    with pytest.raises(ValidationError):
        BookUpdate.model_validate({**valid_book_data(), "member_id": 0})

    updated = BookUpdate.model_validate(
        {**valid_book_data(), "title": "  Updated title  "}
    )
    assert updated.title == "Updated title"
