# ──────────────────────────────────────────────────────────────
# app/models/user.py
# User ORM model — SQLAlchemy 2.0 style.
# ──────────────────────────────────────────────────────────────

import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# TYPE_CHECKING guard avoids circular imports at runtime.
# These strings are resolved only by static type checkers (mypy / pyright).
if TYPE_CHECKING:
    from app.models.health_profile import HealthProfile


# ── Role Enum ──────────────────────────────────────────────────
class UserRole(str, enum.Enum):
    """
    Role-based access control levels.
    Inherits from str so FastAPI can serialize it directly in JSON responses.
    """
    user    = "user"     # Standard wellness user
    admin   = "admin"    # Platform administrator
    trainer = "trainer"  # Future: certified trainer access


# ── User Model ─────────────────────────────────────────────────
class User(Base):
    """
    Core user account model.

    Stores authentication credentials and account metadata.
    Health data, workout plans, and progress live in related tables
    to keep this model lean and focused on identity.
    """

    __tablename__ = "users"

    # ── Primary Key ────────────────────────────────────────────
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    # ── Identity ───────────────────────────────────────────────
    email: Mapped[str] = mapped_column(
        String(320),          # RFC 5321 max email length
        unique=True,
        nullable=False,
        index=True,           # Fast lookups during login
    )

    full_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    # ── Security ───────────────────────────────────────────────
    hashed_password: Mapped[str] = mapped_column(
        String(255),          # bcrypt output is always 60 chars; 255 gives headroom
        nullable=False,
    )

    # ── Role ───────────────────────────────────────────────────
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole", create_constraint=True),
        nullable=False,
        default=UserRole.user,
        server_default=UserRole.user.value,
    )

    # ── Account Status ─────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",   # SQLite uses 1/0; PostgreSQL uses TRUE/FALSE
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",   # Email verification not yet done at registration
    )

    # ── Timestamps (timezone-aware) ────────────────────────────
    # server_default uses DB-side NOW() so records are correct
    # even when inserted outside the ORM (migrations, seeds).
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),  # Automatically refreshed on every UPDATE
    )

    # ── Relationships ──────────────────────────────────────────
    # back_populates links the other side of each relationship.
    # lazy="select" (default) — loads related data only when accessed.
    # uselist=False for one-to-one (health_profile, rewards).

    health_profile: Mapped[Optional["HealthProfile"]] = relationship(
        "HealthProfile",
        back_populates="user",
        uselist=False,         # One user → one health profile
        cascade="all, delete-orphan",
    )

    # ── Composite Indexes ──────────────────────────────────────
    __table_args__ = (
        # Speeds up filtering active users by role (e.g., admin queries)
        Index("ix_users_role_is_active", "role", "is_active"),
    )

    # ── Helpers ────────────────────────────────────────────────
    def __repr__(self) -> str:
        return (
            f"<User id={self.id} email={self.email!r} "
            f"role={self.role.value} active={self.is_active}>"
        )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.admin

    @property
    def is_trainer(self) -> bool:
        return self.role == UserRole.trainer
