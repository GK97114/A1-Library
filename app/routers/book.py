"""HTTP endpoints for books."""

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import (
    ADMIN_RESPONSES,
    AUTHENTICATED_RESPONSES,
    AdminUser,
    CurrentUser,
)
from app.exceptions import (
    BookNotFoundError,
    DuplicateIsbnError,
    MemberNotFoundError,
)
from app.routers.http_errors import book_not_found, duplicate_isbn, member_not_found
from app.dependencies import get_book_service
from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.schemas.errors import ErrorResponse
from app.services.book import BookService

router = APIRouter(prefix="/books", tags=["Books"])

BookServiceDep = Annotated[BookService, Depends(get_book_service)]


@router.get(
    "",
    response_model=list[BookResponse],
    summary="List all books in the library",
    description="Return every book currently stored by the application.",
    responses=AUTHENTICATED_RESPONSES,
)
def list_books(service: BookServiceDep, _current_user: CurrentUser) -> list[Book]:
    """Return every book by retriving it from the service layer."""
    return service.list_books()


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get one book by its ID",
    description="Return the book identified by the path parameter.",
    responses={
        **AUTHENTICATED_RESPONSES,
        404: {"model": ErrorResponse, "description": "Book not found"},
    },
)
def get_book(book_id: int, service: BookServiceDep, _current_user: CurrentUser) -> Book:
    """Return the book from the service layer identified by the path parameter."""
    try:
        return service.get_book(book_id)
    except BookNotFoundError:
        raise book_not_found() from None


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new book",
    description="Create a new book. The member_id must identify an existing member and the ISBN must be unique.",
    responses={
        **ADMIN_RESPONSES,
        404: {"model": ErrorResponse, "description": "Member not found"},
        409: {
            "model": ErrorResponse,
            "description": "A book with this ISBN already exists",
        },
    },
)
def create_book(payload: BookCreate, service: BookServiceDep, _admin_user: AdminUser) -> Book:
    """Create a new book in the service layer."""
    try:
        return service.create_book(payload)
    except MemberNotFoundError:
        raise member_not_found() from None
    except DuplicateIsbnError:
        raise duplicate_isbn() from None


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Update an existing book",
    description="Replace all fields of an existing book. The member_id must identify an existing member and the ISBN must be unique.",
    responses={
        **ADMIN_RESPONSES,
        404: {"model": ErrorResponse, "description": "Book or member not found"},
        409: {
            "model": ErrorResponse,
            "description": "Another book with this ISBN already exists",
        },
    },
)
def replace_book(book_id: int, payload: BookUpdate, service: BookServiceDep, _admin_user: AdminUser) -> Book:
    """Replace an existing book in the service layer."""
    try:
        return service.replace_book(book_id, payload)
    except BookNotFoundError:
        raise book_not_found() from None
    except MemberNotFoundError:
        raise member_not_found() from None
    except DuplicateIsbnError:
        raise duplicate_isbn() from None


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
    description="Remove a book from the library collection, whether or not it is associated with a member.",
    responses={
        **ADMIN_RESPONSES,
        404: {"model": ErrorResponse, "description": "Book not found"},
    },
)
def delete_book(book_id: int, service: BookServiceDep, _admin_user: AdminUser) -> Response:
    try:
        service.delete_book(book_id)
    except BookNotFoundError:
        raise book_not_found() from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)