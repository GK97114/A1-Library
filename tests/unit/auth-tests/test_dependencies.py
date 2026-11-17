"""Unit tests for the authentication dependencies."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.dependencies import get_authenticated_user, require_admin_user
from app.auth.users import AuthenticatedUser, UserRole, get_token_for_role
from app.config import Settings, StorageBackend

# AUTHENTICATION TESTS

@pytest.mark.parametrize(
    ("role", "username"), 
    [(UserRole.ADMIN, "admin_user"), (UserRole.MEMBER, "member_user")],
)
def test_valid_default_token_authenticates_its_users_role(
    role: UserRole,
    username: str,
) -> None:
    """Each configured default token shall resolve to its fixed user and role."""
    settings = Settings(storage_backend=StorageBackend.MEMORY)
    user = get_authenticated_user(
        token_credentials(get_token_for_role(role, settings)), settings
    )
    assert user == AuthenticatedUser(username=username, role=role)

def test_get_user_for_token_returns_none_for_unknown_or_empty_token() -> None:
    """Unknown or empty tokens should not authenticate."""
    settings = Settings(storage_backend=StorageBackend.MEMORY)
    user = get_authenticated_user(token_credentials(""), settings)
    assert user is None

@pytest.mark.parametrize(
        # Create test cases for missing, unknown, and wrong scheme credentials
        "credentials",
        [
            None,
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake_default_access_token"),
            HTTPAuthorizationCredentials(scheme="Basic", credentials="fake_admin_token"),
        ],
        # Provide human-readable IDs for each test case
        ids=["missing", "unknown-token", "wrong-scehme"],
)
def test_get_authenticated_user_rejects_missing_credentials_with_401(credentials: HTTPAuthorizationCredentials | None,) -> None:
    """A missing HTTPAuthorizationCredentials value should raise HTTP 401."""
    settings = Settings(storage_backend=StorageBackend.MEMORY)
    with pytest.raises(HTTPException) as error:
        get_authenticated_user(credentials, settings)
    
    assert error.value.status_code == 401
    assert error.value.detail == "Missing or invalid authentication credentials"
    assert error.value.headers == {"WWW-Authenticate": "Bearer"}

def test_get_authenticated_user_rejects_wrong_scheme_or_token_with_401(
    credentials: HTTPAuthorizationCredentials,
) -> None:
    """Non-Bearer schemes and unknown bearer tokens should raise HTTP 401."""
    settings = Settings(storage_backend=StorageBackend.MEMORY)
    with pytest.raises(HTTPException) as error:
        get_authenticated_user(credentials, settings)

    assert error.value.status_code == 401
    assert error.value.detail == "Missing or invalid authentication credentials"
    assert error.value.headers == {"WWW-Authenticate": "Bearer"}

# AUTHORIZATION TESTS

def test_require_admin_user_allows_admin_and_rejects_member() -> None:
    """A valid member identity receives HTTP 403 when accessing admin-only endpoints."""
    member_user = AuthenticatedUser(username="member", role=UserRole.MEMBER)

    with pytest.raises(HTTPException) as error:
        require_admin_user(member_user)

    assert error.value.status_code == 403
    assert error.value.detail == "Insufficient permissions for this endpoint"

# Helpers

def token_credentials(
        token: str,
        scheme: str = "Bearer",
) -> HTTPAuthorizationCredentials:
    """Build the HTTPAuthorizationCredentials object that FastAPI's security dependencies expect."""
    return HTTPAuthorizationCredentials(scheme=scheme, credentials=token)