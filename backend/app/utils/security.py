# ──────────────────────────────────────────────────────────────
# app/utils/security.py
# Password hashing and JWT token utilities.
# ──────────────────────────────────────────────────────────────

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# ── Password Hashing ───────────────────────────────────────────
# bcrypt with a cost factor of 12 — strong enough for production
# while keeping login latency under ~250 ms on modern hardware.
# deprecated="auto" automatically upgrades weaker hashes on login.

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        plain_password: The raw password from the registration form.

    Returns:
        A bcrypt hash string safe to store in the database.
    """
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password:  Raw password from the login form.
        hashed_password: Stored bcrypt hash from the database.

    Returns:
        True if the password matches, False otherwise.
        Never raises — returns False on any internal error.
    """
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# ── JWT Token Creation ─────────────────────────────────────────

def create_access_token(
    subject: str,
    role: str,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Create a short-lived JWT access token.

    Payload claims:
        sub   — user identifier (user ID as string)
        role  — user role for RBAC checks
        type  — "access" (distinguishes from refresh tokens)
        iat   — issued-at timestamp
        exp   — expiry timestamp

    Args:
        subject:      Unique user identifier (str(user.id)).
        role:         UserRole value ("user" | "admin" | "trainer").
        extra_claims: Optional dict of additional claims to embed.

    Returns:
        Signed JWT string.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload: dict = {
        "sub":  subject,
        "role": role,
        "type": "access",
        "iat":  now,
        "exp":  expire,
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(subject: str, role: str) -> str:
    """
    Create a long-lived JWT refresh token.

    Payload claims:
        sub   — user identifier
        role  — user role
        type  — "refresh" (must be checked before granting a new access token)
        iat   — issued-at timestamp
        exp   — expiry timestamp

    Args:
        subject: Unique user identifier (str(user.id)).
        role:    UserRole value.

    Returns:
        Signed JWT string.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.refresh_token_expire_days)

    payload: dict = {
        "sub":  subject,
        "role": role,
        "type": "refresh",
        "iat":  now,
        "exp":  expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


# ── JWT Token Decoding ─────────────────────────────────────────

class TokenData:
    """
    Structured container for decoded JWT claims.
    Avoids passing raw dicts through the codebase.
    """

    def __init__(self, payload: dict) -> None:
        self.subject: str        = payload["sub"]
        self.role: str           = payload.get("role", "user")
        self.token_type: str     = payload.get("type", "access")
        self.issued_at: datetime = datetime.fromtimestamp(
            payload["iat"], tz=timezone.utc
        )
        self.expires_at: datetime = datetime.fromtimestamp(
            payload["exp"], tz=timezone.utc
        )

    @property
    def user_id(self) -> int:
        """Return the subject claim as an integer user ID."""
        return int(self.subject)

    def __repr__(self) -> str:
        return (
            f"<TokenData user_id={self.user_id} "
            f"role={self.role} type={self.token_type}>"
        )


def decode_token(token: str, expected_type: str = "access") -> TokenData:
    """
    Decode and validate a JWT token.

    Validates:
        - Signature using jwt_secret_key
        - Expiration (exp claim)
        - Token type (access vs refresh)

    Args:
        token:         Raw JWT string from the Authorization header.
        expected_type: "access" or "refresh" — raises if token type mismatches.

    Returns:
        TokenData with decoded claims.

    Raises:
        ValueError: On any validation failure (expired, tampered, wrong type).
                    Callers should map this to HTTP 401.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise ValueError(f"Invalid or expired token: {exc}") from exc

    token_type = payload.get("type")
    if token_type != expected_type:
        raise ValueError(
            f"Wrong token type: expected '{expected_type}', got '{token_type}'"
        )

    if "sub" not in payload:
        raise ValueError("Token is missing required 'sub' claim")

    return TokenData(payload)
