"""HTTP endpoints for members."""

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_member_service
from app.models.book import Book
from app.models.members import Member
from app.schemas.book import BookResponse
from app.schemas.members import MemberCreate, MemberResponse, MemberUpdate
from app.services.members import MemberService

router = APIRouter(prefix="/members", tags=["Members"])

MemberServiceDep = Annotated[MemberService, Depends(get_member_service)]


@router.get(
    "",
    response_model=list[MemberResponse],
    summary="List all members associated with the library",
    description="Return every member currently stored by the application.",
)
def list_members(service: MemberServiceDep) -> list[Member]:
    return service.list_members()


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get one member by their ID",
    description="Return the member identified by the path parameter.",
    responses={404: {"description": "Member not found"}},
)
def get_member(member_id: int, service: MemberServiceDep) -> Member:
    return service.get_member(member_id)


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new member",
    description="Create a new member. The email and membership ID must be unique.",
    responses={409: {"description": "A member with this email or membership ID already exists"}},
)
def create_member(payload: MemberCreate, service: MemberServiceDep) -> Member:
    return service.create_member(payload)


@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Update an existing member",
    description="Replace all fields of an existing member. The email and membership ID must be unique.",
    responses={
        404: {"description": "Member not found"},
        409: {"description": "Another member with this email or membership ID already exists"},
    },
)
def replace_member(
    member_id: int, payload: MemberUpdate, service: MemberServiceDep
) -> Member:
    return service.replace_member(member_id, payload)


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a member",
    description="Remove a member from the library collection. A member who still has books cannot be deleted.",
    responses={
        404: {"description": "Member not found"},
        409: {"description": "Member cannot be deleted because they have books"},
    },
)
def delete_member(member_id: int, service: MemberServiceDep) -> Response:
    service.delete_member(member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    summary="List all books associated with a specific member",
    description="Return every book associated with the specified member.",
    responses={404: {"description": "Member not found"}},
)
def list_member_books(member_id: int, service: MemberServiceDep) -> list[Book]:
    return service.list_member_books(member_id)