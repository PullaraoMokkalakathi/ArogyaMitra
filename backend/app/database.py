# ──────────────────────────────────────────────────────────────
# app/database.py
# SQLAlchemy 2.0 database engine, session, and base setup.
# SQLite (dev) + PostgreSQL-ready (production).
# ──────────────────────────────────────────────────────────────

import logging
from typing import Generator
from urllib.parse import urlparse

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# ── Engine ─────────────────────────────────────────────────────
db_url = settings.database_url

# Normalize PostgreSQL URL for SQLAlchemy 2.0 with psycopg (v3)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Safe diagnostic logging (no credentials or full URL)
try:
    parsed = urlparse(db_url)
    logger.info(
        "Database connection target: driver=%s host=%s port=%s",
        parsed.scheme,
        parsed.hostname,
        parsed.port,
    )
except Exception:
    logger.debug("Could not parse database URL for diagnostic logging")

connect_args: dict = {}
engine_kwargs: dict = {
    "pool_pre_ping": True,         # Verify connections before checkout (handles dropped/stale connections)
    "pool_recycle": settings.db_pool_recycle,  # Recycle connections periodically
    "echo": settings.debug,        # Log SQL statements only in debug mode
}

if settings.is_sqlite:
    # SQLite requires check_same_thread=False for FastAPI multi-threaded requests
    connect_args["check_same_thread"] = False
    engine_kwargs["connect_args"] = connect_args
else:
    # PostgreSQL connection pool settings (for Supabase / Render)
    engine_kwargs.update({
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_timeout": settings.db_pool_timeout,
    })

engine = create_engine(db_url, **engine_kwargs)


# ── SQLite performance pragmas ──────────────────────────────────
# Applied on every new SQLite connection for better performance
# and crash safety. No-op on PostgreSQL connections.

@event.listens_for(engine, "connect")
def set_sqlite_pragmas(dbapi_connection, connection_record):
    """
    Enable WAL mode and enforce foreign key constraints on SQLite.
    WAL (Write-Ahead Logging) improves concurrent read performance.
    """
    if settings.is_sqlite:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


# ── Session Factory ────────────────────────────────────────────
# autocommit=False — transactions must be committed explicitly.
# autoflush=False  — prevents unexpected DB writes mid-request.
# expire_on_commit=False — keeps ORM objects usable after commit
#                          (important for returning response models).

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ── Declarative Base ───────────────────────────────────────────
# All ORM models inherit from this Base.
# Provides the metadata registry and table mapping infrastructure.

class Base(DeclarativeBase):
    pass


# ── Dependency: get_db ─────────────────────────────────────────
# FastAPI dependency that yields a database session per request.
# Guarantees the session is always closed after the request ends,
# even if an exception is raised (finally block).

def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy Session for each incoming request.

    Usage in a FastAPI route:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Database Initialization ────────────────────────────────────
def init_db() -> None:
    """
    Create all tables defined in ORM models if they don't already exist.
    Called once at application startup from main.py.
    Non-destructive: existing tables and data are preserved.
    """
    from app.models import user, health_profile, progress  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        logger.error(f"Failed to auto-create tables: {exc}")
        raise


def check_db_connection() -> bool:
    """
    Verify the database is reachable.
    Used in the /health endpoint for readiness checks.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning(f"Database connectivity check failed: {exc}")
        return False
