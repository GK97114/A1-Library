"""Unit tests for authentication and authorization dependencies."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.dependencies import get_authenticated_user, require_admin_user
from app.auth.users import (
    AuthenticatedUser,
    UserRole,
    get_token_for_role,
    get_user_for_token,
)
from app.config import Settings, StorageBackend


@pytest.mark.parametrize(
    ("role", "username"),
    [(UserRole.ADMIN, "admin"), (UserRole.MEMBER, "member")],
)
def test_valid_default_token_maps_to_its_user_and_role(
    role: UserRole, username: str
) -> None:
    """Verify that a valid default token maps to its corresponding user and role."""
    settings = Settings(storage_backend=StorageBackend.MEMORY)

    user = get_user_for_token(get_token_for_role(role, settings), settings)

    assert user == AuthenticatedUser(username=username, role=role)


@pytest.mark.parametrize("token", ["", "unknown-token"])
def test_get_user_for_token_returns_none_for_unknown_or_empty_token(
    token: str,
) -> None:
    """Verify that get_user_for_token returns None for unknown or empty tokens."""
    settings = Settings(storage_backend=StorageBackend.MEMORY)

    assert get_user_for_token(token, settings) is None


@pytest.mark.parametrize(
    "credentials",
    [
        None,
        HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="unknown-token"
        ),
        HTTPAuthorizationCredentials(scheme="Basic", credentials="admin-default-token"),
    ],
    ids=["missing", "unknown-token", "wrong-scheme"],
)
def test_get_authenticated_user_rejects_missing_or_invalid_credentials(
    credentials: HTTPAuthorizationCredentials | None,
) -> None:
    """Verify that get_authenticated_user rejects missing or invalid credentials."""
    settings = Settings(storage_backend=StorageBackend.MEMORY)

    with pytest.raises(HTTPException) as error:
        get_authenticated_user(credentials, settings)

    assert error.value.status_code == 401
    assert error.value.detail == "Missing or invalid authentication credentials"
    assert error.value.headers == {"WWW-Authenticate": "Bearer"}


def test_require_admin_user_allows_admin() -> None:
    """Verify that require_admin_user allows an admin user."""
    admin = AuthenticatedUser(username="admin", role=UserRole.ADMIN)

    assert require_admin_user(admin) is admin


def test_require_admin_user_rejects_member() -> None:
    """Verify that require_admin_user rejects a member user."""
    member = AuthenticatedUser(username="member", role=UserRole.MEMBER)

    with pytest.raises(HTTPException) as error:
        require_admin_user(member)

    assert error.value.status_code == 403
    assert error.value.detail == "Insufficient permissions for this endpoint"


def token_credentials(
    token: str,
    scheme: str = "Bearer",
) -> HTTPAuthorizationCredentials:
    """Build the HTTP credentials expected by the authentication dependency."""
    return HTTPAuthorizationCredentials(scheme=scheme, credentials=token)
