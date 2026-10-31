import sys
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def test_production_rejects_wildcard_cors(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 64)
        monkeypatch.setenv("CORS_ORIGINS", "*")
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
            assert "wildcard" in str(e).lower() or "cors" in str(e).lower()
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, main
        importlib.reload(config)
        importlib.reload(main)


def test_production_rejects_empty_cors(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 64)
        monkeypatch.setenv("CORS_ORIGINS", "")
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
            assert "cors" in str(e).lower()
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, main
        importlib.reload(config)
        importlib.reload(main)


def test_production_configured_origin_allowed(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 64)
        monkeypatch.setenv("CORS_ORIGINS", "https://myapp.vercel.app")
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
        from fastapi.testclient import TestClient
        with TestClient(main.app) as client:
            resp = client.options("/", headers={"Origin": "https://myapp.vercel.app", "Access-Control-Request-Method": "GET"})
            assert resp.headers.get("access-control-allow-origin") == "https://myapp.vercel.app"
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, database, main
        importlib.reload(config)
        importlib.reload(database)
        importlib.reload(main)


def test_production_unconfigured_vercel_origin_rejected(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 64)
        monkeypatch.setenv("CORS_ORIGINS", "https://myapp.vercel.app")
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
        from fastapi.testclient import TestClient
        with TestClient(main.app) as client:
            resp = client.options("/", headers={"Origin": "https://evil.vercel.app", "Access-Control-Request-Method": "GET"})
            # Should not allow unconfigured vercel origin
            assert resp.headers.get("access-control-allow-origin") != "https://evil.vercel.app"
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, database, main
        importlib.reload(config)
        importlib.reload(database)
        importlib.reload(main)


def test_production_unconfigured_external_origin_rejected(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 64)
        monkeypatch.setenv("CORS_ORIGINS", "https://myapp.vercel.app")
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
        from fastapi.testclient import TestClient
        with TestClient(main.app) as client:
            resp = client.options("/", headers={"Origin": "https://evil.com", "Access-Control-Request-Method": "GET"})
            assert resp.headers.get("access-control-allow-origin") != "https://evil.com"
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        import importlib
        from app import config, database, main
        importlib.reload(config)
        importlib.reload(database)
        importlib.reload(main)


def test_development_localhost_cors():
    from app.main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        resp = client.options("/", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
        # Dev should allow localhost
        assert resp.status_code in [200, 204]
