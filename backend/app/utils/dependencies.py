# ──────────────────────────────────────────────────────────────
# app/utils/dependencies.py
# Reusable FastAPI dependencies for auth and DB access.
# ──────────────────────────────────────────────────────────────

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.security import TokenData, decode_token

# Bearer token extractor — reads Authorization: Bearer <token>
_bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency: extracts and validates the JWT access token.
    Returns the authenticated User ORM object.
    Raises HTTP 401 on any auth failure.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data: TokenData = decode_token(
            credentials.credentials,
            expected_type="access",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user: User | None = db.get(User, token_data.user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact support.",
        )

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency: requires the authenticated user to have admin role.
    Raises HTTP 403 if the user is not an admin.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )
    return current_user
