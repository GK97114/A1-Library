"""Predefined users for authentication and authorization."""

from dataclasses import dataclass
from enum import Enum

from app.config import Settings

class UserRole(str, Enum):
    """Enumeration of user roles supported by the apps permission system."""

    MEMBER = "member"
    ADMIN = "admin"

@dataclass(frozen=True)
class AuthenticatedUser:
    """Represent the identity and role established by a valid HTTP bearer token."""

    username: str
    role: UserRole

def get_user_for_token(token: str, settings: Settings) -> AuthenticatedUser | None:
    """Map one of the predefined bearer tokens to a user identity and role."""
    member_token = get_token_for_role(UserRole.MEMBER, settings)
    admin_token = get_token_for_role(UserRole.ADMIN, settings)

    # Check if enviroment values are not empty and match the provided token
    if member_token and token == member_token:
        return AuthenticatedUser(username="member", role=UserRole.MEMBER)
    if admin_token and token == admin_token:
        return AuthenticatedUser(username="admin", role=UserRole.ADMIN)
    return None

def get_token_for_role(role: UserRole, settings: Settings) -> str:
    """Return the valid bearer token for the given role."""
    if role is UserRole.MEMBER:
        return settings.default_member_token
    return settings.default_admin_token