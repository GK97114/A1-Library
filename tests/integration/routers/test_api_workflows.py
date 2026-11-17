"""FastAPI integration tests for complete Book and Member workflows."""

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
    *,
    member_id: int,
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


def test_memory_backend_completes_member_and_book_workflow(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Verify that the memory backend completes a full member and book workflow."""
    member_response = memory_api_client.post(
        "/members", json=member_payload(), headers=admin_headers
    )
    assert member_response.status_code == 201
    member = member_response.json()
    assert member["id"] > 0

    book_response = memory_api_client.post(
        "/books",
        json=book_payload(member_id=member["id"]),
        headers=admin_headers,
    )
    assert book_response.status_code == 201
    book = book_response.json()
    assert book["id"] > 0

    assert memory_api_client.get(
        f"/members/{member['id']}", headers=admin_headers
    ).json()["id"] == member["id"]
    assert memory_api_client.get(
        f"/books/{book['id']}", headers=admin_headers
    ).json()["title"] == "The Hobbit"
    assert [
        related_book["id"]
        for related_book in memory_api_client.get(
            f"/members/{member['id']}/books", headers=admin_headers
        ).json()
    ] == [book["id"]]

    replacement = book_payload(
        member_id=member["id"], isbn="1234567891", title="Updated title"
    )
    update_response = memory_api_client.put(
        f"/books/{book['id']}", json=replacement, headers=admin_headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated title"

    assert memory_api_client.delete(
        f"/books/{book['id']}", headers=admin_headers
    ).status_code == 204
    assert memory_api_client.delete(
        f"/members/{member['id']}", headers=admin_headers
    ).status_code == 204
    assert memory_api_client.get(
        f"/members/{member['id']}", headers=admin_headers
    ).status_code == 404


def test_database_backend_persists_member_and_book_between_requests(
    database_api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Verify that the database backend persists a member and book between requests."""
    member_response = database_api_client.post(
        "/members", json=member_payload(), headers=admin_headers
    )
    assert member_response.status_code == 201
    member_id = member_response.json()["id"]

    book_response = database_api_client.post(
        "/books",
        json=book_payload(member_id=member_id),
        headers=admin_headers,
    )
    assert book_response.status_code == 201
    book_id = book_response.json()["id"]

    assert database_api_client.get(
        f"/members/{member_id}", headers=admin_headers
    ).json()["id"] == member_id
    assert database_api_client.get(
        f"/books/{book_id}", headers=admin_headers
    ).json()["id"] == book_id
    assert [
        book["id"]
        for book in database_api_client.get(
            f"/members/{member_id}/books", headers=admin_headers
        ).json()
    ] == [book_id]


def test_api_rejects_book_creation_for_missing_member(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Verify that the API rejects book creation for a non-existent member."""
    response = memory_api_client.post(
        "/books",
        json=book_payload(member_id=999),
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_api_returns_empty_book_list_for_member_without_books(
    memory_api_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Verify that the API returns an empty book list for a member without books."""
    response = memory_api_client.post(
        "/members", json=member_payload(), headers=admin_headers
    )
    assert response.status_code == 201

    books_response = memory_api_client.get(
        f"/members/{response.json()['id']}/books", headers=admin_headers
    )

    assert books_response.status_code == 200
    assert books_response.json() == []
