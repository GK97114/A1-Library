"""HTTP negative tests for request and path-parameter validation."""

from datetime import date
from typing import Any

import pytest
from httpx import Response
from starlette.testclient import TestClient

# Helper functions for building request payloads and asserting validation errors.

def book_payload() -> dict[str, Any]:
    """Return a valid Book body that an individual test can make invalid."""
    return {
        "title": "The Hobbit",
        "author": "J. R. R. Tolkien",
        "isbn": "1234567890",
        "published_year": 1937,
        "member_id": 1,
    }


def member_payload() -> dict[str, str]:
    """Return a valid Member body that an individual test can make invalid."""
    return {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "membership_id": "M-001",
        "phone": "(555)-123-4567",
    }


def assert_validation_error(
    client: TestClient,
    response: Response,
    operation_path: str,
    method: str,
    expected_location: list[str],
) -> None:
    """Check a 422 response against its documented HTTPValidationError schema."""
    assert response.status_code == 422

    document = client.get("/openapi.json").json()
    response_schema = document["paths"][operation_path][method]["responses"]["422"][
        "content"
    ]["application/json"]["schema"]
    assert response_schema["$ref"] == "#/components/schemas/HTTPValidationError"

    body = response.json()
    validation_schema = document["components"]["schemas"]["HTTPValidationError"]
    assert set(body) == {"detail"}
    assert set(body) <= set(validation_schema["properties"])
    detail_schema = validation_schema["properties"]["detail"]
    assert detail_schema["type"] == "array"
    assert isinstance(body["detail"], list)
    assert body["detail"]

    error_schema = document["components"]["schemas"]["ValidationError"]
    required_error_fields = set(error_schema["required"])
    assert detail_schema["items"]["$ref"] == "#/components/schemas/ValidationError"
    assert all(
        required_error_fields <= set(error)
        for error in body["detail"]
    )
    assert any(
        error["loc"] == expected_location
        for error in body["detail"]
    )

# Tests for Book resource validation errors.

@pytest.mark.parametrize(
    "field",
    ["title", "author", "isbn", "published_year", "member_id"],
)
def test_api_rejects_each_missing_required_book_field(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
    field: str,
) -> None:
    """A missing required Book field returns a 422 validation error."""
    payload = book_payload()
    del payload[field]

    response = memory_api_client.post(
        "/books",
        json=payload,
        headers=admin_headers,
    )

    assert_validation_error(
        memory_api_client,
        response,
        "/books",
        "post",
        ["body", field],
    )


def test_api_rejects_unknown_book_fields(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """An unknown Book field returns a 422 validation error."""
    payload = {**book_payload(), "unexpected": "value"}

    response = memory_api_client.post(
        "/books",
        json=payload,
        headers=admin_headers,
    )

    assert_validation_error(
        memory_api_client,
        response,
        "/books",
        "post",
        ["body", "unexpected"],
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("title", "T" * 201),
        ("author", ""),
        ("author", "A" * 121),
        ("isbn", "1" * 9),
        ("isbn", "1" * 18),
        ("published_year", 1449),
        ("published_year", date.today().year + 1),
        ("member_id", 0),
        ("member_id", -1),
    ],
)
def test_api_rejects_book_field_values_outside_schema_boundaries(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
    field: str,
    value: Any,
) -> None:
    """A Book field value outside the schema boundaries returns a 422 validation error."""
    response = memory_api_client.post(
        "/books",
        json={**book_payload(), field: value},
        headers=admin_headers,
    )

    assert_validation_error(
        memory_api_client,
        response,
        "/books",
        "post",
        ["body", field],
    )


@pytest.mark.parametrize(
    "field",
    ["name", "email", "membership_id", "phone"],
)
def test_api_rejects_each_missing_required_member_field(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
    field: str,
) -> None:
    """A missing required Member field returns a 422 validation error."""
    payload = member_payload()
    del payload[field]

    response = memory_api_client.post(
        "/members",
        json=payload,
        headers=admin_headers,
    )

    assert_validation_error(
        memory_api_client,
        response,
        "/members",
        "post",
        ["body", field],
    )


def test_api_rejects_unknown_member_fields(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """An unknown Member field returns a 422 validation error."""
    payload = {**member_payload(), "unexpected": "value"}

    response = memory_api_client.post(
        "/members",
        json=payload,
        headers=admin_headers,
    )

    assert_validation_error(
        memory_api_client,
        response,
        "/members",
        "post",
        ["body", "unexpected"],
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("name", "N" * 121),
        ("email", "not-an-email"),
        ("email", f"a@{'b' * 63}.{'c' * 31}.com"),
        ("membership_id", "M" * 21),
        ("phone", "555-123-4567"),
        ("phone", "(555)-123-456"),
    ],
)
def test_api_rejects_member_values_outside_schema_boundaries(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
    field: str,
    value: str,
) -> None:
    """A Member field value outside the schema boundaries returns a 422 validation error."""
    response = memory_api_client.post(
        "/members",
        json={**member_payload(), field: value},
        headers=admin_headers,
    )

    assert_validation_error(
        memory_api_client,
        response,
        "/members",
        "post",
        ["body", field],
    )

@pytest.mark.parametrize(
    ("method", "request_path", "operation_path", "path_parameter", "payload"),
    [
        ("GET", "/books/not-an-id", "/books/{book_id}", "book_id", None),
        (
            "PUT",
            "/books/not-an-id",
            "/books/{book_id}",
            "book_id",
            book_payload(),
        ),
        ("DELETE", "/books/not-an-id", "/books/{book_id}", "book_id", None),
        ("GET", "/members/not-an-id", "/members/{member_id}", "member_id", None),
        (
            "PUT",
            "/members/not-an-id",
            "/members/{member_id}",
            "member_id",
            member_payload(),
        ),
        (
            "DELETE",
            "/members/not-an-id",
            "/members/{member_id}",
            "member_id",
            None,
        ),
        (
            "GET",
            "/members/not-an-id/books",
            "/members/{member_id}/books",
            "member_id",
            None,
        ),
    ],
    ids=[
        "get-book",
        "replace-book",
        "delete-book",
        "get-member",
        "replace-member",
        "delete-member",
        "get-member-books",
    ],
)
def test_api_rejects_invalid_book_and_member_path_id_types(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
    method: str,
    request_path: str,
    operation_path: str,
    path_parameter: str,
    payload: dict[str, Any] | None,
) -> None:
    """An invalid path ID type returns a 422 validation error."""
    request_kwargs: dict[str, Any] = {"headers": admin_headers}
    if payload is not None:
        request_kwargs["json"] = payload

    response = memory_api_client.request(method, request_path, **request_kwargs)

    assert_validation_error(
        memory_api_client,
        response,
        operation_path,
        method.lower(),
        ["path", path_parameter],
    )
