"""Pydantic schemas used for documented HTTP error responses."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Describe the JSON body returned for an HTTP error."""
    # Used to describe the error message returned in the response body.
    detail: str
