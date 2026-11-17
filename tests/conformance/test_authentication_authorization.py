"""Conformance tests for the published OpenAPI security contract."""

from app.main import app


def test_openapi_declares_the_bearer_auth_scheme() -> None:
    schema = app.openapi()

    assert schema["components"]["securitySchemes"]["BearerAuth"] == {
        "type": "http",
        "scheme": "bearer",
    }


def test_openapi_marks_only_protected_operations_with_bearer_security() -> None:
    """Verify that only protected operations are marked with bearer security."""
    schema = app.openapi()
    paths = schema["paths"]

    assert "security" not in paths["/"]["get"]
    assert "security" not in paths["/health"]["get"]

    for path, path_item in paths.items():
        if path.startswith(("/books", "/members")):
            for operation in path_item.values():
                if isinstance(operation, dict) and "responses" in operation:
                    assert operation["security"] == [{"BearerAuth": []}]


def test_openapi_marks_mutating_operations_as_admin_protected() -> None:
    """Verify that mutating operations are marked as admin protected."""
    schema = app.openapi()

    for path, path_item in schema["paths"].items():
        if not path.startswith(("/books", "/members")):
            continue
        for method in ("post", "put", "delete"):
            operation = path_item.get(method)
            if operation is not None:
                assert operation["security"] == [{"BearerAuth": []}]
                assert "401" in operation["responses"]
                assert "403" in operation["responses"]


def test_openapi_publishes_authentication_responses_for_protected_reads() -> None:
    """Verify that protected read operations publish authentication responses."""
    schema = app.openapi()

    for path, path_item in schema["paths"].items():
        if not path.startswith(("/books", "/members")):
            continue
        for method in ("get",):
            operation = path_item.get(method)
            if operation is not None:
                assert "401" in operation["responses"]
