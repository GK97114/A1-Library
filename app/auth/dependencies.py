"""FastAPI dependencies for authentication and authorization."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings
from app.dependencies import get_settings
from app.auth.users import AuthneticatedUser, UserRole, get_user_for_token

bearer_scheme = HTTPBearer(auto_error=False, scheme_name="BearerAuth")
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]

UNAUTHORIZED_RESPONSE = {
    "description": "Missing or invalid token",
    "headers": {
        "WWW-Authenticate": {
            "description": "Authentication scheme required by this endpoint.",
            "schema": {"type": "string"},
        }
    },
}
FORBIDDEN_RESPONSE = {"description": "Insufficient permissions for this endpoint."}
AUTHENTICATED_RESPONSES = {401: UNAUTHORIZED_RESPONSE}
ADMIN_RESPONSES = {401: UNAUTHORIZED_RESPONSE, 403: FORBIDDEN_RESPONSE}

def missing_authentication() -> HTTPException:
    """Build the exception for missing or invalid authentication credentials."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

AppSettings = Annotated[Settings, Depends(get_settings)]

def get_authenticated_user(
    credentials: BearerCredentials, settings: AppSettings
) -> AuthneticatedUser:
    """Return the user identity and role established by a valid HTTP bearer token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise missing_authentication()
    user = get_user_for_token(credentials.credentials, settings)
    if user is None:
        raise missing_authentication()
    return user

CurrentUser = Annotated[AuthneticatedUser, Depends(get_authenticated_user)]

def require_admin_user(session_user: CurrentUser) -> AuthneticatedUser:
    """Return the user identity and role established by a valid HTTP bearer token, requiring admin privileges."""
    if session_user.role is not UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this endpoint",
        )
    return session_user

AdminUser = Annotated[AuthneticatedUser, Depends(require_admin_user)]