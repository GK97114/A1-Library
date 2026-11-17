"""HTTP negative tests for API business rules and data integrity."""

import pytest
from httpx import Response
from starlette.testclient import TestClient


BACKEND_FIXTURES = ["memory_api_client", "database_api_client"]
BACKEND_IDS = ["memory", "postgres"]

# Helper functions for building request payloads and creating resources.

def api_client_for_backend(
    request: pytest.FixtureRequest,
    backend_fixture: str,
) -> TestClient:
    """Get the isolated API client selected by a parametrized test."""
    return request.getfixturevalue(backend_fixture)


def member_payload(
    *,
    name: str = "Ada Lovelace",
    email: str = "ada@example.com",
    membership_id: str = "M-001",
) -> dict[str, str]:
    """Build a valid Member request body, allowing unique test values."""
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
    """Build a valid Book request body for an existing member."""
    return {
        "title": title,
        "author": "J. R. R. Tolkien",
        "isbn": isbn,
        "published_year": 1937,
        "member_id": member_id,
    }


def create_member(
    client: TestClient,
    headers: dict[str, str],
    payload: dict[str, str],
) -> dict[str, object]:
    """Create a Member and return its response body."""
    response = client.post("/members", json=payload, headers=headers)

    assert response.status_code == 201
    return response.json()


def create_book(
    client: TestClient,
    headers: dict[str, str],
    payload: dict[str, object],
) -> dict[str, object]:
    """Create a Book and return its response body."""
    response = client.post("/books", json=payload, headers=headers)

    assert response.status_code == 201
    return response.json()


def assert_error_response(
    response: Response,
    status_code: int,
    detail: str,
) -> None:
    """Check the documented HTTP status and JSON detail response."""
    assert response.status_code == status_code
    assert response.json() == {"detail": detail}

@pytest.mark.parametrize(
    "backend_fixture",
    BACKEND_FIXTURES,
    ids=BACKEND_IDS,
)
def test_api_returns_documented_404_for_missing_book(
    request: pytest.FixtureRequest,
    backend_fixture: str,
    admin_headers: dict[str, str],
) -> None:
    """A missing Book returns 404 without changing the Book collection."""
    client = api_client_for_backend(request, backend_fixture)

    response = client.get("/books/999999", headers=admin_headers)

    assert_error_response(response, 404, "Book not found")
    assert client.get("/books", headers=admin_headers).json() == []


@pytest.mark.parametrize(
    "backend_fixture",
    BACKEND_FIXTURES,
    ids=BACKEND_IDS,
)
def test_api_returns_documented_404_for_missing_member(
    request: pytest.FixtureRequest,
    backend_fixture: str,
    admin_headers: dict[str, str],
) -> None:
    """A missing Member returns 404 without changing the Member collection."""
    client = api_client_for_backend(request, backend_fixture)

    response = client.get("/members/999999", headers=admin_headers)

    assert_error_response(response, 404, "Member not found")
    assert client.get("/members", headers=admin_headers).json() == []


@pytest.mark.parametrize(
    "backend_fixture",
    BACKEND_FIXTURES,
    ids=BACKEND_IDS,
)
def test_api_rejects_book_for_nonexistent_member_without_storing_it(
    request: pytest.FixtureRequest,
    backend_fixture: str,
    admin_headers: dict[str, str],
) -> None:
    """A Book cannot be created for a Member that does not exist."""
    client = api_client_for_backend(request, backend_fixture)

    response = client.post(
        "/books",
        json=book_payload(999999),
        headers=admin_headers,
    )

    assert_error_response(response, 404, "Member not found")
    assert client.get("/books", headers=admin_headers).json() == []


@pytest.mark.parametrize(
    "backend_fixture",
    BACKEND_FIXTURES,
    ids=BACKEND_IDS,
)
def test_api_rejects_duplicate_isbn_without_changing_books(
    request: pytest.FixtureRequest,
    backend_fixture: str,
    admin_headers: dict[str, str],
) -> None:
    """A duplicate ISBN returns 409 and leaves the existing Book unchanged."""
    client = api_client_for_backend(request, backend_fixture)
    member = create_member(client, admin_headers, member_payload())
    book = create_book(
        client,
        admin_headers,
        book_payload(member["id"]),
    )

    duplicate_response = client.post(
        "/books",
        json=book_payload(member["id"], title="Duplicate copy"),
        headers=admin_headers,
    )

    assert_error_response(
        duplicate_response,
        409,
        "A book with this ISBN already exists",
    )
    assert client.get("/books", headers=admin_headers).json() == [book]


@pytest.mark.parametrize(
    "backend_fixture",
    BACKEND_FIXTURES,
    ids=BACKEND_IDS,
)
def test_api_rejects_duplicate_member_email_without_changing_members(
    request: pytest.FixtureRequest,
    backend_fixture: str,
    admin_headers: dict[str, str],
) -> None:
    """A duplicate email returns 409 and leaves the existing Member unchanged."""
    client = api_client_for_backend(request, backend_fixture)
    member = create_member(client, admin_headers, member_payload())
    duplicate_payload = member_payload(
        name="Different Member",
        membership_id="M-002",
    )

    duplicate_response = client.post(
        "/members",
        json=duplicate_payload,
        headers=admin_headers,
    )

    assert_error_response(
        duplicate_response,
        409,
        "A member with this email or membership ID already exists",
    )
    assert client.get("/members", headers=admin_headers).json() == [member]


@pytest.mark.parametrize(
    "backend_fixture",
    BACKEND_FIXTURES,
    ids=BACKEND_IDS,
)
def test_api_rejects_duplicate_membership_id_without_changing_members(
    request: pytest.FixtureRequest,
    backend_fixture: str,
    admin_headers: dict[str, str],
) -> None:
    """A duplicate membership ID returns 409 without adding another Member."""
    client = api_client_for_backend(request, backend_fixture)
    member = create_member(client, admin_headers, member_payload())
    duplicate_payload = member_payload(
        name="Different Member",
        email="different@example.com",
    )

    duplicate_response = client.post(
        "/members",
        json=duplicate_payload,
        headers=admin_headers,
    )

    assert_error_response(
        duplicate_response,
        409,
        "A member with this email or membership ID already exists",
    )
    assert client.get("/members", headers=admin_headers).json() == [member]


@pytest.mark.parametrize(
    "backend_fixture",
    BACKEND_FIXTURES,
    ids=BACKEND_IDS,
)
def test_api_rejects_member_deletion_while_books_are_linked(
    request: pytest.FixtureRequest,
    backend_fixture: str,
    admin_headers: dict[str, str],
) -> None:
    """A Member with Books cannot be deleted, and the relationship remains."""
    client = api_client_for_backend(request, backend_fixture)
    member = create_member(client, admin_headers, member_payload())
    book = create_book(
        client,
        admin_headers,
        book_payload(member["id"]),
    )

    response = client.delete(
        f"/members/{member['id']}",
        headers=admin_headers,
    )

    assert_error_response(
        response,
        409,
        "Delete or reassign the member's books before deleting the member",
    )
    assert client.get(
        f"/members/{member['id']}", headers=admin_headers
    ).json() == member
    assert client.get(
        f"/books/{book['id']}", headers=admin_headers
    ).json() == book
    assert client.get(
        f"/members/{member['id']}/books", headers=admin_headers
    ).json() == [book]


@pytest.mark.parametrize(
    "backend_fixture",
    BACKEND_FIXTURES,
    ids=BACKEND_IDS,
)
def test_api_rejects_duplicate_values_on_replace_without_mutating_records(
    request: pytest.FixtureRequest,
    backend_fixture: str,
    admin_headers: dict[str, str],
) -> None:
    """Conflicting Book and Member replacements return 409 without mutation."""
    client = api_client_for_backend(request, backend_fixture)

    first_member = create_member(
        client,
        admin_headers,
        member_payload(),
    )
    second_member = create_member(
        client,
        admin_headers,
        member_payload(
            name="Grace Hopper",
            email="grace@example.com",
            membership_id="M-002",
        ),
    )
    first_book = create_book(
        client,
        admin_headers,
        book_payload(first_member["id"]),
    )
    second_book = create_book(
        client,
        admin_headers,
        book_payload(
            second_member["id"],
            isbn="1234567891",
            title="Another book",
        ),
    )

    duplicate_isbn_response = client.put(
        f"/books/{first_book['id']}",
        json=book_payload(
            first_member["id"],
            isbn=second_book["isbn"],
            title="Conflicting replacement",
        ),
        headers=admin_headers,
    )
    assert_error_response(
        duplicate_isbn_response,
        409,
        "A book with this ISBN already exists",
    )

    duplicate_email_response = client.put(
        f"/members/{first_member['id']}",
        json=member_payload(
            name="Conflicting replacement",
            email=second_member["email"],
            membership_id="M-003",
        ),
        headers=admin_headers,
    )
    assert_error_response(
        duplicate_email_response,
        409,
        "A member with this email or membership ID already exists",
    )

    duplicate_membership_id_response = client.put(
        f"/members/{first_member['id']}",
        json=member_payload(
            name="Conflicting replacement",
            email="updated@example.com",
            membership_id=second_member["membership_id"],
        ),
        headers=admin_headers,
    )
    assert_error_response(
        duplicate_membership_id_response,
        409,
        "A member with this email or membership ID already exists",
    )

    assert client.get(
        f"/books/{first_book['id']}", headers=admin_headers
    ).json() == first_book
    assert client.get(
        f"/books/{second_book['id']}", headers=admin_headers
    ).json() == second_book
    assert client.get(
        f"/members/{first_member['id']}", headers=admin_headers
    ).json() == first_member
    assert client.get(
        f"/members/{second_member['id']}", headers=admin_headers
    ).json() == second_member
