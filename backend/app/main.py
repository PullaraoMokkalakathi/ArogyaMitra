# ──────────────────────────────────────────────────────────────
# main.py
# ArogyaMitra FastAPI application entry point.
# Initializes the app, middleware, rate limiting, and routes.
# ──────────────────────────────────────────────────────────────
from app.config import settings

print("GROQ KEY:", settings.groq_api_key[:15] if settings.groq_api_key else "NOT FOUND")
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

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
# Uses client IP address as the rate-limit key.
# The limiter instance is shared across all routers via app.state.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_general],
)


# ── Lifespan ───────────────────────────────────────────────────
# Replaces deprecated @app.on_event("startup").
# Runs startup logic before the first request, cleanup on shutdown.

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────
    logger.info("━" * 60)
    logger.info(f"  {settings.app_name} v{settings.app_version} starting up")
    logger.info(f"  Environment : {settings.environment}")
    logger.info(f"  Debug mode  : {settings.debug}")
    logger.info(f"  Database    : {settings.database_url}")
    logger.info("━" * 60)

    # Create all database tables
    try:
        init_db()
        logger.info("✓ Database tables initialized successfully")
    except Exception as exc:
        logger.critical(f"✗ Database initialization failed: {exc}")
        raise

    yield  # Application runs here

    # ── Shutdown ───────────────────────────────────────────────
    logger.info(f"  {settings.app_name} shutting down gracefully")


# ── FastAPI Application ────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "ArogyaMitra – Adaptive AI Health & Wellness Coach. "
        "Enterprise-grade multi-agent AI platform for personalized "
        "workout generation, nutrition planning, and wellness coaching."
    ),
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc UI
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ── Rate Limiter State ─────────────────────────────────────────
# Attach limiter to app.state so slowapi can discover it.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── CORS Middleware ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TEMP FIX
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handlers ──────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all for unhandled exceptions.
    Returns a safe error response — never exposes stack traces in production.
    """
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)

    # In debug mode return the error message; in production return a generic message.
    detail = str(exc) if settings.debug else "An internal server error occurred."

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": detail,
            "path": str(request.url),
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": "NOT_FOUND",
            "message": f"Route {request.url.path} does not exist.",
        },
    )


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        content={
            "success": False,
            "error": "METHOD_NOT_ALLOWED",
            "message": f"Method {request.method} is not allowed on this endpoint.",
        },
    )


# ── Root Endpoint ──────────────────────────────────────────────
@app.get("/", tags=["Root"], summary="API root")
async def root():
    """
    Root endpoint — confirms the API is live.
    """
    return {
        "success": True,
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# ── Health Check Endpoint ──────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Service health check")
async def health_check():
    """
    Readiness probe for load balancers and deployment platforms.
    Returns API status, database connectivity, environment info, and version.
    """
    db_ok = check_db_connection()

    overall_status = "healthy" if db_ok else "degraded"
    http_status = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=http_status,
        content={
            "success": db_ok,
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "app": {
                "name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment,
                "debug": settings.debug,
            },
            "services": {
                "database": "connected" if db_ok else "unreachable",
            },
        },
    )


# ── API v1 Router Registration ─────────────────────────────────
# Routers are registered here under the /api/v1 prefix.
# Each router is imported only after its module is created
# to avoid circular import errors during incremental development.

API_V1_PREFIX = "/api/v1"

# ── Auth Router ───────────────────────────────────────────────
from app.routers import auth
app.include_router(auth.router, prefix="/api/v1")

# ── Health Profile Router ──────────────────────────────────────
from app.routers import health
app.include_router(health.router, prefix="/api/v1")

# ── Workout Router ────────────────────────────────────────────────
from app.routers import workout
app.include_router(workout.router, prefix="/api/v1")

# ── Posture Router ────────────────────────────────────────────────
from app.routers import posture
app.include_router(posture.router, prefix="/api/v1")

# ── Nutrition Router ──────────────────────────────────────────────
from app.routers import nutrition
app.include_router(nutrition.router, prefix="/api/v1")

# ── Progress Router ───────────────────────────────────────────────
from app.routers import progress
app.include_router(progress.router, prefix="/api/v1")

# ── AI Router ──────────────────────────────
from app.routers import ai
app.include_router(ai.router, prefix="/api/v1")

logger.info("Router registration placeholder ready — uncomment as each router is added.")
