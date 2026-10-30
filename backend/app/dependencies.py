# ──────────────────────────────────────────────────────────────
# app/dependencies.py
# Application-wide FastAPI dependencies.
# Import from here in all routers — not from utils/dependencies.py.
# ──────────────────────────────────────────────────────────────

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.security import TokenData, decode_token

logger = logging.getLogger(__name__)

# ── Bearer Token Extractor ─────────────────────────────────────
# auto_error=True → FastAPI returns 403 automatically when the
# Authorization header is missing entirely (before our code runs).
_bearer_scheme = HTTPBearer(auto_error=True)


# ── get_current_user ───────────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extracts the Bearer token from the Authorization header,
    decodes and validates the JWT, then loads the User from the DB.

    Raises:
        HTTP 401 — token missing, malformed, expired, or tampered.
        HTTP 401 — user ID in token does not exist in the database.
    """
    try:
        token_data: TokenData = decode_token(
            credentials.credentials,
            expected_type="access",
        )
    except ValueError as exc:
        logger.warning(f"Token validation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user: User | None = db.get(User, token_data.user_id)

    if user is None:
        logger.warning(f"Token references non-existent user_id={token_data.user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ── get_current_active_user ────────────────────────────────────

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Extends get_current_user by enforcing the is_active flag.
    Deactivated accounts are authenticated but forbidden from
    accessing any protected resource.

    Raises:
        HTTP 403 — account exists but is_active=False.
    """
    if not current_user.is_active:
        logger.warning(
            f"Deactivated user attempted access: id={current_user.id} "
            f"email={current_user.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Contact support.",
        )

    return current_user


# ── get_current_admin_user ─────────────────────────────────────

def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Extends get_current_active_user by enforcing admin role.
    Use this dependency on all admin-only endpoints.

    Raises:
        HTTP 403 — authenticated and active but role != admin.
    """
    if current_user.role != UserRole.admin:
        logger.warning(
            f"Non-admin access attempt: id={current_user.id} "
            f"email={current_user.email} role={current_user.role.value}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required to access this resource.",
        )

    return current_user
