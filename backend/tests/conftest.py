import os
import tempfile
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend root in path
BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import Base, get_db
from app import main


@pytest.fixture(scope="function")
def temp_db_file():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        yield path
    finally:
        try:
            # Windows may hold file handles; try to remove
            os.unlink(path)
        except Exception:
            pass


@pytest.fixture(scope="function")
def test_app(temp_db_file):
    test_db_url = f"sqlite:///{temp_db_file}"
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator:
        db = TestingSessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    original_overrides = dict(main.app.dependency_overrides)
    main.app.dependency_overrides[get_db] = override_get_db
    original_init_db = getattr(main, "init_db", None)
    main.init_db = lambda: None

    import app.database as db_module
    original_check = db_module.check_db_connection
    original_main_check = getattr(main, "check_db_connection", None)

    def test_check_db_connection():
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    db_module.check_db_connection = test_check_db_connection
    main.check_db_connection = test_check_db_connection

    try:
        yield main.app
    finally:
        if original_init_db is not None:
            main.init_db = original_init_db
        else:
            try:
                delattr(main, "init_db")
            except Exception:
                pass
        db_module.check_db_connection = original_check
        if original_main_check is not None:
            main.check_db_connection = original_main_check
        else:
            try:
                delattr(main, "check_db_connection")
            except Exception:
                pass
        main.app.dependency_overrides = original_overrides
        try:
            engine.dispose()
        except Exception:
            pass


@pytest.fixture(scope="function")
def client(test_app):
    with TestClient(test_app) as c:
        yield c
