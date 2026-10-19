from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.storage import books, members

router = APIRouter(prefix="/books", tags=["Books"])

def find_book(book_id: int) -> BookResponse:
    """Helper function to find a book by its ID."""
    for book in books:
        if book.id == book_id:
            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book with ID {book_id} not found"
    )

def ensure_member_exists(member_id: int) -> None:
    """Raise 404 if the referenced member does not exist."""
    if not any(member.id == member_id for member in members):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found"
        )

def normalize_isbn(isbn: str) -> str:
    """Remove hyphens and spaces and uppercase, so formatting differences still match."""
    return isbn.replace("-", "").replace(" ", "").upper()

def ensure_unique_isbn(isbn: str, exclude_book_id: int | None = None) -> None:
    """Raise 409 if another book already uses this ISBN."""
    normalized_isbn = normalize_isbn(isbn)
    for existing in books:
        if existing.id != exclude_book_id and normalize_isbn(existing.isbn) == normalized_isbn:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A book with {isbn} already exists",
            )

# GET /books reads the entire list collection of books
@router.get(
    "",
    response_model=list[BookResponse],
    summary="List all books in the library",
    description="Return every book currently stored by the application."
)
def list_books() -> list[BookResponse]:
    """Return the entire list of books stored in memory"""
    return books

# GET /books/{book_id} searches for a single book by its ID
@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get one book by its ID",
    description="Return the book identified by the path parameter.",
    responses={404: {"description": "Book not found"}}
)
def get_book(book_id: int) -> BookResponse:
    """Return the book with the requested book ID."""
    return find_book(book_id)

# POST /books creates a new book and adds it to the library collection
@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new book",
    description="Create a new book from the validated fields.",
    responses={
        404: {"description": "Referenced member not found"},
        409: {"description": "A book with the same ISBN already exists"},
    }
)
def create_book(payload: BookCreate) -> BookResponse:
    """Create a new book and add it to the in-memory collection."""
    # Validate that the referenced member exists and that the ISBN is unique
    ensure_member_exists(payload.member_id)
    ensure_unique_isbn(payload.isbn)

    next_book_id = max((book.id for book in books), default=0) +1
    new_book = BookResponse(
        id=next_book_id,
        **payload.model_dump(),
    )
    books.append(new_book)
    return new_book

# PUT /books/{book_id} updates an existing book by its ID
@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Update an existing book",
    description="Replace all fields of an existing book.",
    responses={
        404: {"description": "Book not found"},
        409: {"description": "A book with the same ISBN already exists"},
    },
)
def replace_book(
    book_id: int,
    payload: BookUpdate,
) -> BookResponse:
    """Replace an existing book with new data."""
    bookToEdit = find_book(book_id)
    # Validate that the referenced member exists and that the ISBN is unique (excluding the current book)
    ensure_member_exists(payload.member_id)
    ensure_unique_isbn(payload.isbn, exclude_book_id=book_id)

    updated_book = BookResponse(
        id=book_id,
        **payload.model_dump(),
    )
    books[books.index(bookToEdit)] = updated_book
    return updated_book

# DELETE /books/{book_id} removes a book from the library collection
@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
    description="Remove a book from the library collection.",
    responses={
        404: {"description": "Book not found"},
    },
)
def delete_book(book_id: int) -> Response:
    """Delete a book from the in-memory collection."""
    books.remove(find_book(book_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)