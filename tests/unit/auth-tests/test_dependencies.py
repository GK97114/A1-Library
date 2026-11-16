"""Unit tests for the authentication dependencies."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.dependencies import get_authenticated_user, require_admin_user
from app.auth.users import AuthneticatedUser, UserRole, get_token_for_role
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
    assert user == AuthneticatedUser(username=username, role=role)

# Helpers

def token_credentials(
        token: str,
        scheme: str = "Bearer",
) -> HTTPAuthorizationCredentials:
    """Build the HTTPAuthorizationCredentials object that FastAPI's security dependencies expect."""
    return HTTPAuthorizationCredentials(scheme=scheme, credentials=token)

# Additional unit-test outlines:
#
# test_get_user_for_token_maps_each_configured_token_to_its_role
#   Check the member and admin tokens map to the corresponding fixed username
#   and UserRole.
#
# test_get_user_for_token_returns_none_for_unknown_or_empty_token
#   Check values other than the configured nonempty tokens do not authenticate.
#
# test_get_authenticated_user_rejects_missing_credentials_with_401
#   Check a missing HTTPAuthorizationCredentials value raises HTTP 401.
#
# test_get_authenticated_user_rejects_wrong_scheme_or_token_with_401
#   Check non-Bearer schemes and unknown bearer tokens raise HTTP 401.
#
# test_require_admin_user_allows_admin_and_rejects_member
#   Check an admin user is returned unchanged and a member user raises HTTP 403.