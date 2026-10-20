"""Translate application outcomes into HTTP responses for API routes."""

from fastapi import HTTPException, status


def book_not_found() -> HTTPException:
    """Return the HTTP 404 response for a missing Book."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found",
    )


def member_not_found() -> HTTPException:
    """Return the HTTP 404 response for a missing Member."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Member not found",
    )


def duplicate_isbn() -> HTTPException:
    """Return the HTTP 409 response for a duplicate ISBN."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="A book with this ISBN already exists",
    )


def duplicate_member() -> HTTPException:
    """Return the HTTP 409 response for a duplicate email or membership ID."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="A member with this email or membership ID already exists",
    )


def member_has_books() -> HTTPException:
    """Return the HTTP 409 response for a Member who still has Books."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Delete or reassign the member's books before deleting the member",
    )