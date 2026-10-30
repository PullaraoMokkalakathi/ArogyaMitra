# ──────────────────────────────────────────────────────────────
# app/schemas/auth.py
# Pydantic v2 schemas for authentication endpoints.
# ──────────────────────────────────────────────────────────────

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


# ── Helpers ────────────────────────────────────────────────────

_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
)


def _validate_password_strength(password: str) -> str:
    """
    Shared password strength validator.
    Raises ValueError with a clear message on failure.
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")
    return password


# ── Request Schemas ────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    """
    Payload for POST /api/v1/auth/register.
    Validates email format, password strength, and confirmation match.
    """

    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=150,
        examples=["Arjun Sharma"],
    )

    email: EmailStr = Field(
        ...,
        examples=["arjun@example.com"],
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["SecurePass1"],
    )

    confirm_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["SecurePass1"],
    )

    @model_validator(mode="after")
    def validate_passwords(self) -> "UserRegisterRequest":
        """Validates password strength and confirm_password match."""
        # Strength check
        _validate_password_strength(self.password)

        # Confirmation match
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")

        return self


class UserLoginRequest(BaseModel):
    """
    Payload for POST /api/v1/auth/login.
    """

    email: EmailStr = Field(
        ...,
        examples=["arjun@example.com"],
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        examples=["SecurePass1"],
    )


class RefreshTokenRequest(BaseModel):
    """
    Payload for POST /api/v1/auth/refresh.
    Sends a valid refresh token to obtain a new access token.
    """

    refresh_token: str = Field(
        ...,
        min_length=10,
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )


# ── Response Schemas ───────────────────────────────────────────

class TokenResponse(BaseModel):
    """
    Returned on successful login or token refresh.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """
    Safe public representation of a User record.
    Never includes hashed_password or internal fields.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime


class AuthResponse(BaseModel):
    """
    Combined response returned on successful registration or login.
    Bundles the token pair together with the user profile.
    """

    success: bool = True
    message: str
    tokens: TokenResponse
    user: UserResponse
