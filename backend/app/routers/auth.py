# ──────────────────────────────────────────────────────────────
# app/routers/auth.py  — Part 1
# Register and Login endpoints.
# ──────────────────────────────────────────────────────────────

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    AuthResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Internal helper ────────────────────────────────────────────

def _make_token_pair(user: User) -> TokenResponse:
    """Build an access + refresh token pair for a given user."""
    return TokenResponse(
        access_token=create_access_token(
            subject=str(user.id),
            role=user.role.value,
        ),
        refresh_token=create_refresh_token(
            subject=str(user.id),
            role=user.role.value,
        ),
        token_type="bearer",
    )


# ── POST /register ─────────────────────────────────────────────

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    responses={
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"},
    },
)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Create a new user account.

    Steps:
    1. Check for duplicate email.
    2. Hash the password with bcrypt.
    3. Insert the User row, flush to catch race-condition duplicates.
    4. Commit, refresh, and return tokens + user profile.
    """
    # ── 1. Duplicate email check ───────────────────────────────
    existing: User | None = (
        db.query(User).filter(User.email == payload.email).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # ── 2. Build user record ───────────────────────────────────
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=UserRole.user,          # Default role is always "user"
        is_active=True,
        is_verified=False,
    )

    # ── 3. Persist ─────────────────────────────────────────────
    try:
        db.add(user)
        db.flush()       # Assigns user.id; raises IntegrityError on duplicate
        db.commit()
        db.refresh(user) # Reloads server-side defaults (created_at, etc.)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    logger.info(f"User registered: id={user.id} email={user.email}")

    # ── 4. Return response ─────────────────────────────────────
    return AuthResponse(
        success=True,
        message="Account created successfully. Welcome to ArogyaMitra!",
        tokens=_make_token_pair(user),
        user=UserResponse.model_validate(user),
    )


# ── POST /login ────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    responses={
        401: {"description": "Invalid email or password"},
        403: {"description": "Account deactivated"},
    },
)
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Authenticate a user and return a JWT token pair.

    Uses a constant-time dummy verify when user is not found
    to prevent user-enumeration via response timing.
    """
    # Generic error reused for both "not found" and "wrong password"
    _bad_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # ── 1. Lookup user ─────────────────────────────────────────
    user: User | None = (
        db.query(User).filter(User.email == payload.email).first()
    )

    # ── 2. Verify password (runs even when user is None) ───────
    # Running bcrypt on a dummy hash ensures response time is
    # identical whether the email exists or not — prevents
    # user enumeration via timing side-channel.
    stored_hash = user.hashed_password if user else "$2b$12$dummyhashusedtopreventimenumeration"
    password_ok = verify_password(payload.password, stored_hash)

    if user is None or not password_ok:
        raise _bad_credentials

    # ── 3. Active account check ────────────────────────────────
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact support.",
        )

    logger.info(f"User logged in: id={user.id} email={user.email}")

    # ── 4. Return tokens ───────────────────────────────────────
    return AuthResponse(
        success=True,
        message="Login successful. Welcome back!",
        tokens=_make_token_pair(user),
        user=UserResponse.model_validate(user),
    )


# ── POST /refresh ────────────────────────────────────────────

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtain a new access token using a refresh token",
    responses={
        401: {"description": "Invalid, expired, or wrong token type"},
    },
)
def refresh(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Exchange a valid refresh token for a new access token.

    - Only refresh tokens are accepted (access tokens are rejected).
    - The user is re-verified against the DB on every refresh.
    - Returns a new access token only (refresh token stays the same).
    """
    # ── 1. Decode & validate as refresh token only ────────────────
    try:
        token_data = decode_token(payload.refresh_token, expected_type="refresh")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # ── 2. Re-validate user still exists and is active ─────────────
    user: User | None = db.get(User, token_data.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact support.",
        )

    # ── 3. Issue new access token only ───────────────────────────
    new_access_token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
    )

    logger.info(f"Access token refreshed: user_id={user.id}")

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=payload.refresh_token,  # Return same refresh token
        token_type="bearer",
    )


# ── GET /me ───────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the currently authenticated user's profile",
    responses={
        401: {"description": "Missing or invalid access token"},
        403: {"description": "Account deactivated"},
    },
)
def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Returns the authenticated user's public profile.

    Requires a valid Bearer access token.
    Deactivated accounts receive HTTP 403 before reaching this handler.
    """
    return UserResponse.model_validate(current_user)
