"""HTTP endpoints for members."""

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import (
    ADMIN_RESPONSES,
    AUTHENTICATED_RESPONSES,
    AdminUser,
    CurrentUser,
)

from app.dependencies import get_member_service
from app.exceptions import ConflictError, MemberHasBooksError, MemberNotFoundError
from app.models.book import Book
from app.models.members import Member
from app.routers.http_errors import duplicate_member, member_has_books, member_not_found
from app.schemas.book import BookResponse
from app.schemas.errors import ErrorResponse
from app.schemas.members import MemberCreate, MemberResponse, MemberUpdate
from app.services.members import MemberService

router = APIRouter(prefix="/members", tags=["Members"])

MemberServiceDep = Annotated[MemberService, Depends(get_member_service)]


@router.get(
    "",
    response_model=list[MemberResponse],
    summary="List all members associated with the library",
    description="Return every member currently stored by the application.",
    responses=AUTHENTICATED_RESPONSES,
    
)
def list_members(service: MemberServiceDep, _current_user: CurrentUser) -> list[Member]:
    """Return every member from the service layer."""
    return service.list_members()


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get one member by their ID",
    description="Return the member identified by the path parameter.",
    responses={
        **AUTHENTICATED_RESPONSES,
        404: {"model": ErrorResponse, "description": "Member not found"},
    },
)
def get_member(member_id: int, service: MemberServiceDep, _current_user: CurrentUser) -> Member:
    """Return the member from the service layer identified by the path parameter."""
    try:
        return service.get_member(member_id)
    except MemberNotFoundError:
        raise member_not_found() from None


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new member",
    description="Create a new member. The email and membership ID must be unique.",
    responses={
            **ADMIN_RESPONSES,
            409: {
                "model": ErrorResponse,
                "description": "A member with this email or membership ID already exists",
            },
        },
)
def create_member(payload: MemberCreate, service: MemberServiceDep, _admin_user: AdminUser) -> Member:
    """Create a new member in the service layer."""
    try:
        return service.create_member(payload)
    except ConflictError:
        raise duplicate_member() from None


@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Update an existing member",
    description="Replace all fields of an existing member. The email and membership ID must be unique.",
    responses={
        **ADMIN_RESPONSES,
        404: {"model": ErrorResponse, "description": "Member not found"},
        409: {
            "model": ErrorResponse,
            "description": "Another member with this email or membership ID already exists",
        },
    },
)
def replace_member(
    member_id: int, payload: MemberUpdate, service: MemberServiceDep, _admin_user: AdminUser
) -> Member:
    """Replace an existing member in the service layer."""
    try:
        return service.replace_member(member_id, payload)
    except MemberNotFoundError:
        raise member_not_found() from None
    except ConflictError:
        raise duplicate_member() from None


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a member",
    description="Remove a member from the library collection. A member who still has books cannot be deleted.",
    responses={
        **ADMIN_RESPONSES,
        404: {"model": ErrorResponse, "description": "Member not found"},
        409: {
            "model": ErrorResponse,
            "description": "Member cannot be deleted because they have books",
        },
    },
)
def delete_member(member_id: int, service: MemberServiceDep, _admin_user: AdminUser) -> Response:
    """Delete a member from the service layer."""
    try:
        service.delete_member(member_id)
    except MemberNotFoundError:
        raise member_not_found() from None
    except MemberHasBooksError:
        raise member_has_books() from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    summary="List all books associated with a specific member",
    description="Return every book associated with the specified member.",
    responses={
            **AUTHENTICATED_RESPONSES,
            404: {"model": ErrorResponse, "description": "Member not found"},
        },
)
def list_member_books(member_id: int, service: MemberServiceDep, _current_user: CurrentUser) -> list[Book]:
    """Return every book associated with the member ID from the service layer."""
    try:
        return service.list_member_books(member_id)
    except MemberNotFoundError:
        raise member_not_found() from None