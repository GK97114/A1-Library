from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.schemas.members import MemberCreate, MemberResponse, MemberUpdate
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
    response={404: {"description": "Book not found"}}
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
    description="Create a new book from the validated fields."
)
def create_book(book: BookCreate) -> BookResponse:
    """Create a new book and add it to the in-memory collection."""
    next_book_id = max((book.id for book in books), default=0) +1
    new_book = BookResponse(
        id=next_book_id,
        **book.model_dump(),
    )
    books.append(new_book)
    return new_book

# PUT /books/{book_id} updates an existing book by its ID
@router.put(
    "/{book_id}",
    reponse_model=BookResponse,
    summary="Update an existing book",
    description="Replace all fields of an existing book.",
    response={404: {"description": "Book not found"}},
)
def replace_book(
    book_id: int,
    data: BookUpdate,
) -> BookResponse:
    """Replace an existing book with new data."""
    bookToEdit = find_book(book_id)
    updated_book = BookResponse(
        id=book_id,
        **data.model_dump(),
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
        409: {"description": "Book is currently borrowed and cannot be deleted until returned."},
    },
)
def delete_book(book_id: int) -> Response:
    """Delete a book from the in-memory collection."""
    bookToDelete = find_book(book_id)

    if any(member.id == bookToDelete.member_id for member in members):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with ID {book_id} is currently borrowed and cannot be deleted until returned."
        )
    books.remove(bookToDelete)
    return Response(status_code=status.HTTP_204_NO_CONTENT)