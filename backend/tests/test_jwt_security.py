import sys
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def test_production_rejects_insecure_secret(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET_KEY", "arogya-mitra-insecure-dev-secret-key-change-in-production-12345")
        from app import config
        import importlib
        importlib.reload(config)
        from app import main
        import importlib
        importlib.reload(main)
        try:
            import asyncio
            async def test():
                async with main.lifespan(main.app):
                    pass
            asyncio.run(test())
            assert False, "Should have raised exception"
        except RuntimeError as e:
            msg = str(e)
            assert "JWT_SECRET_KEY" in msg or "secret" in msg.lower()
            assert "insecure" in msg.lower() or "default" in msg.lower()
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, main
        importlib.reload(config)
        importlib.reload(main)


def test_production_rejects_missing_secret(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        from app import config
        import importlib
        importlib.reload(config)
        from app import main
        import importlib
        importlib.reload(main)
        try:
            import asyncio
            async def test():
                async with main.lifespan(main.app):
                    pass
            asyncio.run(test())
            assert False, "Should have raised exception"
        except RuntimeError as e:
            assert "JWT_SECRET_KEY" in str(e)
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, main
        importlib.reload(config)
        importlib.reload(main)


def test_production_rejects_empty_secret(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET_KEY", "   ")
        from app import config
        import importlib
        importlib.reload(config)
        from app import main
        import importlib
        importlib.reload(main)
        try:
            import asyncio
            async def test():
                async with main.lifespan(main.app):
                    pass
            asyncio.run(test())
            assert False, "Should have raised exception"
        except RuntimeError as e:
            assert "JWT_SECRET_KEY" in str(e)
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, main
        importlib.reload(config)
        importlib.reload(main)


def test_production_rejects_short_secret(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET_KEY", "short")
        from app import config
        import importlib
        importlib.reload(config)
        from app import main
        import importlib
        importlib.reload(main)
        try:
            import asyncio
            async def test():
                async with main.lifespan(main.app):
                    pass
            asyncio.run(test())
            assert False, "Should have raised exception"
        except RuntimeError as e:
            assert "32" in str(e)
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, main
        importlib.reload(config)
        importlib.reload(main)


def test_production_accepts_strong_secret(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 64)
        from app import config
        import importlib
        importlib.reload(config)
        from app import database
        import importlib
        importlib.reload(database)
        from app import main
        import importlib
        importlib.reload(main)
        main.init_db = lambda: None
        import asyncio
        async def test():
            async with main.lifespan(main.app):
                pass
        asyncio.run(test())
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, database, main
        importlib.reload(config)
        importlib.reload(database)
        importlib.reload(main)


def test_development_accepts_fallback(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("JWT_SECRET_KEY", "arogya-mitra-insecure-dev-secret-key-change-in-production-12345")
        from app import config
        import importlib
        importlib.reload(config)
        from app import database
        import importlib
        importlib.reload(database)
        from app import main
        import importlib
        importlib.reload(main)
        main.init_db = lambda: None
        import asyncio
        async def test():
            async with main.lifespan(main.app):
                pass
        asyncio.run(test())
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, database, main
        importlib.reload(config)
        importlib.reload(database)
        importlib.reload(main)
