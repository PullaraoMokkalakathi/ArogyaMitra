# ──────────────────────────────────────────────────────────────
# app/database.py
# SQLAlchemy 2.0 database engine, session, and base setup.
# SQLite (dev) + PostgreSQL-ready (production).
# ──────────────────────────────────────────────────────────────

from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


# ── Engine ─────────────────────────────────────────────────────
# SQLite requires check_same_thread=False to allow FastAPI's
# async threadpool to share the same connection across threads.
# For PostgreSQL, this argument is ignored entirely.

connect_args: dict = {}

if settings.is_sqlite:
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    # Pool settings tuned for both SQLite (dev) and PostgreSQL (prod).
    pool_pre_ping=True,       # Verify connections before use (handles stale connections)
    pool_recycle=1800,        # Recycle connections every 30 mins
    echo=settings.debug,      # Log SQL statements only in debug mode
)


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
    Create all tables defined in ORM models.
    Called once at application startup from main.py.

    Import all models before calling this so SQLAlchemy
    discovers them and includes them in Base.metadata.
    """
    # Import models here to register them with Base.metadata
    from app.models import user, health_profile  # noqa: F401

    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """
    Verify the database is reachable.
    Used in the /health endpoint for readiness checks.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
