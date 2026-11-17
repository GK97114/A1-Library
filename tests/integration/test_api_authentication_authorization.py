"""API-level authentication and authorization integration tests."""

import pytest
from starlette.testclient import TestClient


def member_payload(
    *,
    name: str = "Ada Lovelace",
    email: str = "ada@example.com",
    membership_id: str = "M-001",
) -> dict[str, str]:
    return {
        "name": name,
        "email": email,
        "membership_id": membership_id,
        "phone": "(555)-123-4567",
    }


def book_payload(
    member_id: int,
    *,
    isbn: str = "1234567890",
    title: str = "The Hobbit",
) -> dict[str, object]:
    return {
        "title": title,
        "author": "J. R. R. Tolkien",
        "isbn": isbn,
        "published_year": 1937,
        "member_id": member_id,
    }


def test_public_health_routes_do_not_require_authentication(
    memory_api_client: TestClient,
) -> None:
    assert memory_api_client.get("/").status_code == 200
    assert memory_api_client.get("/health").status_code == 200


@pytest.mark.parametrize("path", ["/books", "/members"])
@pytest.mark.parametrize(
    "headers",
    [None, {"Authorization": "Bearer invalid-token"}],
    ids=["missing-token", "invalid-token"],
)
def test_protected_read_routes_reject_missing_or_invalid_tokens(
    memory_api_client: TestClient,
    path: str,
    headers: dict[str, str] | None,
) -> None:
    """Verify that protected read routes reject missing or invalid tokens."""
    response = memory_api_client.get(path, headers=headers)

    assert response.status_code == 401


def test_member_token_can_read_but_cannot_write(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
    member_headers: dict[str, str],
) -> None:
    """Verify that a member token can read but cannot write."""
    member_response = memory_api_client.post(
        "/members", json=member_payload(), headers=admin_headers
    )
    assert member_response.status_code == 201
    member_id = member_response.json()["id"]
    book_response = memory_api_client.post(
        "/books", json=book_payload(member_id), headers=admin_headers
    )
    assert book_response.status_code == 201
    book_id = book_response.json()["id"]

    assert memory_api_client.get("/books", headers=member_headers).status_code == 200

    write_requests = [
        ("post", "/members", member_payload()),
        ("post", "/books", book_payload(member_id, isbn="1234567891")),
        ("put", f"/members/{member_id}", member_payload(name="Updated")),
        ("delete", f"/members/{member_id}", None),
        ("put", f"/books/{book_id}", book_payload(member_id, title="Updated")),
        ("delete", f"/books/{book_id}", None),
    ]
    for method, path, payload in write_requests:
        response = memory_api_client.request(
            method.upper(),
            path, json=payload, headers=member_headers
        )
        assert response.status_code == 403


def test_admin_token_can_create_and_update_members_and_books(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Verify that an admin token can create and update members and books."""
    member_response = memory_api_client.post(
        "/members", json=member_payload(), headers=admin_headers
    )
    assert member_response.status_code == 201
    member_id = member_response.json()["id"]

    member_update = member_payload(
        name="Updated Member",
        email="updated@example.com",
        membership_id="M-002",
    )
    updated_member_response = memory_api_client.put(
        f"/members/{member_id}", json=member_update, headers=admin_headers
    )
    assert updated_member_response.status_code == 200
    assert updated_member_response.json()["name"] == "Updated Member"

    book_response = memory_api_client.post(
        "/books", json=book_payload(member_id), headers=admin_headers
    )
    assert book_response.status_code == 201
    book_id = book_response.json()["id"]

    updated_book_response = memory_api_client.put(
        f"/books/{book_id}",
        json=book_payload(member_id, isbn="1234567891", title="Updated Book"),
        headers=admin_headers,
    )
    assert updated_book_response.status_code == 200
    assert updated_book_response.json()["title"] == "Updated Book"


@pytest.mark.parametrize(
    "headers",
    [None, {"Authorization": "Bearer invalid-token"}],
    ids=["missing-token", "invalid-token"],
)
def test_authentication_failures_include_bearer_challenge(
    memory_api_client: TestClient,
    headers: dict[str, str] | None,
) -> None:
    """Verify that authentication failures include the Bearer challenge."""
    response = memory_api_client.get("/books", headers=headers)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
