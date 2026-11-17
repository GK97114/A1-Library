"""Conformance tests for the generated OpenAPI API contract."""

from typing import Any

import pytest
from openapi_spec_validator import validate
from starlette.testclient import TestClient


def get_openapi_document(client: TestClient) -> dict[str, Any]:
    """Fetch the generated OpenAPI document from the application."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    return response.json()


def assert_response_model(
    document: dict[str, Any],
    path: str,
    method: str,
    status_code: int,
    model_name: str,
    *,
    is_array: bool = False,
) -> None:
    """Assert a response uses the named component schema, optionally as a list."""
    response = document["paths"][path][method]["responses"][str(status_code)]
    schema = response["content"]["application/json"]["schema"]

    if is_array:
        assert schema["type"] == "array"
        schema = schema["items"]

    assert schema["$ref"] == f"#/components/schemas/{model_name}"


def assert_request_model(
    document: dict[str, Any],
    path: str,
    method: str,
    model_name: str,
) -> None:
    """Assert a JSON request body references the named component schema."""
    operation = document["paths"][path][method]
    request_body = operation["requestBody"]

    assert request_body["required"] is True
    schema = request_body["content"]["application/json"]["schema"]
    assert schema["$ref"] == f"#/components/schemas/{model_name}"


def assert_error_body_matches_schema(
    document: dict[str, Any],
    response: Any,
    status_code: int,
) -> None:
    """Check an HTTP error body conforms to the documented ErrorResponse shape."""
    assert response.status_code == status_code
    error_schema = document["components"]["schemas"]["ErrorResponse"]
    body = response.json()

    assert set(body) == set(error_schema["required"])
    assert all(
        isinstance(body[field], str)
        for field, definition in error_schema["properties"].items()
        if definition["type"] == "string"
    )


def test_generated_openapi_document_passes_spec_validator(
    memory_api_client: TestClient,
) -> None:
    """Validate the generated document against its declared OpenAPI version."""
    document = get_openapi_document(memory_api_client)

    validate(document)


def test_openapi_publishes_book_operations_and_schemas(
    memory_api_client: TestClient,
) -> None:
    """Check Book methods, request schemas, and success response schemas."""
    document = get_openapi_document(memory_api_client)
    paths = document["paths"]

    assert set(paths["/books"]) == {"get", "post"}
    assert set(paths["/books/{book_id}"]) == {"get", "put", "delete"}

    assert_response_model(document, "/books", "get", 200, "BookResponse", is_array=True)
    assert_request_model(document, "/books", "post", "BookCreate")
    assert_response_model(document, "/books", "post", 201, "BookResponse")

    assert_response_model(
        document, "/books/{book_id}", "get", 200, "BookResponse"
    )
    assert_request_model(document, "/books/{book_id}", "put", "BookUpdate")
    assert_response_model(
        document, "/books/{book_id}", "put", 200, "BookResponse"
    )
    assert "204" in paths["/books/{book_id}"]["delete"]["responses"]
    assert "content" not in paths["/books/{book_id}"]["delete"]["responses"]["204"]


def test_openapi_publishes_member_operations_and_schemas(
    memory_api_client: TestClient,
) -> None:
    """Check Member methods, request schemas, and success response schemas."""
    document = get_openapi_document(memory_api_client)
    paths = document["paths"]

    assert set(paths["/members"]) == {"get", "post"}
    assert set(paths["/members/{member_id}"]) == {"get", "put", "delete"}
    assert set(paths["/members/{member_id}/books"]) == {"get"}

    assert_response_model(
        document, "/members", "get", 200, "MemberResponse", is_array=True
    )
    assert_request_model(document, "/members", "post", "MemberCreate")
    assert_response_model(document, "/members", "post", 201, "MemberResponse")

    assert_response_model(
        document, "/members/{member_id}", "get", 200, "MemberResponse"
    )
    assert_request_model(
        document, "/members/{member_id}", "put", "MemberUpdate"
    )
    assert_response_model(
        document, "/members/{member_id}", "put", 200, "MemberResponse"
    )
    assert "204" in paths["/members/{member_id}"]["delete"]["responses"]
    assert "content" not in paths["/members/{member_id}"]["delete"]["responses"]["204"]

    assert_response_model(
        document,
        "/members/{member_id}/books",
        "get",
        200,
        "BookResponse",
        is_array=True,
    )


def test_openapi_documents_success_and_error_statuses_for_each_operation(
    memory_api_client: TestClient,
) -> None:
    """Check each operation advertises its success and applicable error statuses."""
    document = get_openapi_document(memory_api_client)
    expected_statuses = {
        ("/books", "get"): {"200", "401"},
        ("/books", "post"): {"201", "401", "403", "404", "409", "422"},
        ("/books/{book_id}", "get"): {"200", "401", "404", "422"},
        ("/books/{book_id}", "put"): {
            "200",
            "401",
            "403",
            "404",
            "409",
            "422",
        },
        ("/books/{book_id}", "delete"): {
            "204",
            "401",
            "403",
            "404",
            "422",
        },
        ("/members", "get"): {"200", "401"},
        ("/members", "post"): {"201", "401", "403", "409", "422"},
        ("/members/{member_id}", "get"): {"200", "401", "404", "422"},
        ("/members/{member_id}", "put"): {
            "200",
            "401",
            "403",
            "404",
            "409",
            "422",
        },
        ("/members/{member_id}", "delete"): {
            "204",
            "401",
            "403",
            "404",
            "409",
            "422",
        },
        ("/members/{member_id}/books", "get"): {
            "200",
            "401",
            "404",
            "422",
        },
    }

    for (path, method), required_statuses in expected_statuses.items():
        actual_statuses = set(document["paths"][path][method]["responses"])
        assert required_statuses <= actual_statuses


@pytest.mark.parametrize(
    ("schema_name", "required_fields"),
    [
        (
            "BookCreate",
            {"title", "author", "isbn", "published_year", "member_id"},
        ),
        (
            "BookUpdate",
            {"title", "author", "isbn", "published_year", "member_id"},
        ),
        (
            "BookResponse",
            {"id", "title", "author", "isbn", "published_year", "member_id"},
        ),
        (
            "MemberCreate",
            {"name", "email", "membership_id", "phone"},
        ),
        (
            "MemberUpdate",
            {"name", "email", "membership_id", "phone"},
        ),
        (
            "MemberResponse",
            {"id", "name", "email", "membership_id", "phone"},
        ),
    ],
)
def test_openapi_schemas_declare_expected_required_fields(
    memory_api_client: TestClient,
    schema_name: str,
    required_fields: set[str],
) -> None:
    """Check the OpenAPI components require the fields declared by Pydantic."""
    document = get_openapi_document(memory_api_client)
    schema = document["components"]["schemas"][schema_name]

    assert set(schema["required"]) == required_fields
    assert set(schema["properties"]) == required_fields


def test_openapi_validation_errors_publish_http_validation_error_schema(
    memory_api_client: TestClient,
) -> None:
    """Check typed request and path inputs document the standard 422 schema."""
    document = get_openapi_document(memory_api_client)
    validation_operations = [
        ("/books", "post"),
        ("/books/{book_id}", "get"),
        ("/books/{book_id}", "put"),
        ("/books/{book_id}", "delete"),
        ("/members", "post"),
        ("/members/{member_id}", "get"),
        ("/members/{member_id}", "put"),
        ("/members/{member_id}", "delete"),
        ("/members/{member_id}/books", "get"),
    ]

    for path, method in validation_operations:
        assert_response_model(document, path, method, 422, "HTTPValidationError")


def test_openapi_domain_error_schemas_match_http_error_bodies(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Check documented 404/409 bodies have the same detail shape as the API."""
    document = get_openapi_document(memory_api_client)
    error_operations = [
        ("/books/{book_id}", "get", "404"),
        ("/books", "post", "404"),
        ("/books", "post", "409"),
        ("/books/{book_id}", "put", "404"),
        ("/books/{book_id}", "put", "409"),
        ("/books/{book_id}", "delete", "404"),
        ("/members/{member_id}", "get", "404"),
        ("/members", "post", "409"),
        ("/members/{member_id}", "put", "404"),
        ("/members/{member_id}", "put", "409"),
        ("/members/{member_id}", "delete", "404"),
        ("/members/{member_id}", "delete", "409"),
        ("/members/{member_id}/books", "get", "404"),
    ]

    for path, method, status_code in error_operations:
        assert_response_model(
            document, path, method, int(status_code), "ErrorResponse"
        )

    error_schema = document["components"]["schemas"]["ErrorResponse"]
    assert error_schema["required"] == ["detail"]
    assert error_schema["properties"]["detail"]["type"] == "string"

    missing_book_response = memory_api_client.get(
        "/books/999999", headers=admin_headers
    )
    assert_error_body_matches_schema(document, missing_book_response, 404)

    member_payload = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "membership_id": "M-001",
        "phone": "(555)-123-4567",
    }
    created_member = memory_api_client.post(
        "/members", json=member_payload, headers=admin_headers
    )
    assert created_member.status_code == 201

    duplicate_member_response = memory_api_client.post(
        "/members", json=member_payload, headers=admin_headers
    )
    assert_error_body_matches_schema(document, duplicate_member_response, 409)
