from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.members import MemberCreate, MemberResponse, MemberUpdate
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.storage import books, members

router = APIRouter(prefix="/members", tags=["Members"])

def find_member(member_id: int) -> MemberResponse:
    """Helper function to find a member by their ID."""
    for member in members:
        if member.id == member_id:
            return member

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Member with ID {member_id} not found"
    )

# GET /members reads the entire list collection of members.
@router.get(
    "",
    response_model=list[MemberResponse],
    summary="List all members associated with the library.",
    description="Return every member currently stored by the application.",
)
def list_members() -> list[MemberResponse]:
    """Return every memeber currently stored in memory."""
    return members

# GET /members/{member_id} searches for a single member by their ID.
@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get one member by their ID",
    description="Return the memeber identified by the path parameter.",
    response={404: {"description": "Member not found"}}
)
def get_member(member_id: int) -> MemberResponse:
    """Return the member with the requested member ID."""
    return find_member(member_id)

# POST /members creates a new member and adds them to the library collection.
@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new member",
    description="Create a new member from the validated fields."
)
def create_member(member: MemberCreate) -> MemberResponse:
    """Create a new member and add them into the in-memory collection."""
    next_member_id = max((member.id for member in members), default=0) + 1
    new_member = MemberResponse(
        id=next_member_id,
        **member.model_dump(), # Unpack the validated fields from the request body into the new member object
    )
    members.append(new_member)
    return new_member

# PUT /members/{member_id} updates an existing member by their ID.
@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Update an existing member",
    description="Replace all fields of an existing member.",
    response={404: {"description": "Member not found"}},
)
def replace_member(
    member_id: int,
    member_data: MemberUpdate,
) -> MemberResponse:
    """Replace the member with the requested member ID with the new data."""
    member = find_member(member_id)
    updated_member = MemberResponse(
        id=member_id,
        **member_data.model_dump(),  # Unpack the validated fields from the request body into the updated member object
    )
    members[members.index(member)] = updated_member
    return updated_member

# DELETE /members/{member_id} removes a member from the library collection.
@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a member",
    description="Remove a member from the library collection.",
    responses={
        404: {"description": "Member not found"},
        409: {"description": "Member cannot be deleted because they have borrowed books."}
    },
)
def delete_member(member_id: int) -> Response:
    """Delete the member with the requested member ID."""
    member = find_member(member_id)

    if any(book.member_id == member_id for book in books):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Member with ID {member_id} cannot be deleted because they have borrowed books."
        )

    members.remove(member)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# GET /members/{member_id}/books retrieves all books borrowed by a specific member.
@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    summary="List all books borrowed by a specific member",
    description="Return every book currently borrowed by the specified member.",
    response={404: {"description": "Member not found"}},
)
def list_member_books(member_id: int) -> list[BookResponse]:
    """Return every book currently borrowed by the specified member."""
    find_member(member_id)  # Ensure the member exists
    return [book for book in books if book.member_id == member_id]