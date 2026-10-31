# ──────────────────────────────────────────────────────────────
# main.py
# ArogyaMitra FastAPI application entry point.
# ──────────────────────────────────────────────────────────────
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.database import check_db_connection, init_db

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Rate Limiter ───────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_general],
)


# ── Lifespan ───────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("━" * 60)
    logger.info(f"  {settings.app_name} v{settings.app_version} starting up")
    logger.info(f"  Environment : {settings.environment}")
    logger.info(f"  Port        : {settings.port}")
    
    # Safe database hostname/port logging (no credentials, full URL, or query params)
    try:
        db_url = settings.database_url
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        parsed = urlparse(db_url)
        logger.info(f"  Database    : {parsed.hostname}:{parsed.port}")
        logger.info(
            "Database connection target: driver=%s host=%s port=%s",
            parsed.scheme,
            parsed.hostname,
            parsed.port,
        )
    except Exception:
        logger.debug("Could not parse database host/port for logging")
    
    logger.info(f"  CORS Origins: {settings.cors_origins_list}")
    logger.info("━" * 60)

    if settings.is_production:
        secret = settings.jwt_secret_key or ""
        if not secret.strip():
            raise RuntimeError("JWT_SECRET_KEY must be set in production environment")
        if "insecure-dev" in secret.lower() or secret == "arogya-mitra-insecure-dev-secret-key-change-in-production-12345":
            raise RuntimeError("Insecure default JWT_SECRET_KEY is not allowed in production. Generate a strong secret key.")
        if len(secret) < 32:
            raise RuntimeError("JWT_SECRET_KEY must be at least 32 characters long in production")
        prod_origins = settings.cors_origins_list
        if not prod_origins:
            raise RuntimeError("CORS_ORIGINS must be explicitly configured in production (no wildcard allowed)")
        if "*" in prod_origins:
            raise RuntimeError("Wildcard CORS origins are not allowed in production")

    try:
        init_db()
        logger.info("✓ Database initialized successfully")
    except Exception as exc:
        logger.error(f"✗ Database initialization error: {exc}")
        if not settings.is_production:
            raise
        logger.warning("Continuing startup in production — verify database migrations with lembic upgrade head.")

    yield
    logger.info(f"  {settings.app_name} shutting down gracefully")


# ── FastAPI Application ────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ArogyaMitra – Adaptive AI Health & Wellness Coach.",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = settings.cors_origins_list
is_production = settings.is_production
allow_credentials = True
cors_origins_to_allow = origins

if not is_production and ("*" in origins or not origins):
    cors_origins_to_allow = ["*"]
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_to_allow,
    allow_origin_regex=None,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    detail = str(exc) if settings.debug else "An internal server error occurred."
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"success": False, "error": "INTERNAL_SERVER_ERROR", "message": detail, "path": str(request.url)})


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"success": False, "error": "NOT_FOUND", "message": f"Route {request.url.path} does not exist."})


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, content={"success": False, "error": "METHOD_NOT_ALLOWED", "message": f"Method {request.method} is not allowed on this endpoint."})


@app.get("/", tags=["Root"], summary="API root")
async def root():
    return {"success": True, "message": f"Welcome to {settings.app_name} API", "version": settings.app_version, "docs": "/docs" if not settings.is_production else "disabled in production", "health": "/health"}


@app.get("/health", tags=["Health"], summary="Service health check")
async def health_check():
    db_ok = check_db_connection()
    overall_status = "healthy" if db_ok else "degraded"
    http_status = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=http_status, content={"success": db_ok, "status": overall_status, "timestamp": datetime.now(timezone.utc).isoformat(), "app": {"name": settings.app_name, "version": settings.app_version, "environment": settings.environment, "debug": settings.debug}, "services": {"database": "connected" if db_ok else "unreachable"}})


API_V1_PREFIX = "/api/v1"
from app.routers import auth, health, workout, posture, nutrition, progress, ai
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(health.router, prefix=API_V1_PREFIX)
app.include_router(workout.router, prefix=API_V1_PREFIX)
app.include_router(posture.router, prefix=API_V1_PREFIX)
app.include_router(nutrition.router, prefix=API_V1_PREFIX)
app.include_router(progress.router, prefix=API_V1_PREFIX)
app.include_router(ai.router, prefix=API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
