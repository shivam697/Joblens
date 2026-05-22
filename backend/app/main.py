"""
JobLense API — Main Application Entry Point

This is the FastAPI application that ties everything together:
- CORS middleware for React frontend communication
- Session middleware for OAuth state management
- All API routers mounted under /api/v1
- Startup/shutdown events for scheduler and indexes
- Global exception handler for consistent error responses
"""

import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings, get_missing_required_settings
from app.core.scheduler import start_scheduler, stop_scheduler
from app.db.mysql import create_tables

try:
    from app.db.mongodb import create_mongodb_indexes
except Exception:
    create_mongodb_indexes = None

# Import all routers
from app.api.v1.auth import router as auth_router
from app.api.v1.resume import router as resume_router
from app.api.v1.ats import router as ats_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.recommendations import router as recommendations_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ── Create FastAPI Application ───────────────────────────
app = FastAPI(
    title="JobLense API",
    description="AI-powered job application tracker with ATS analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Session Middleware ───────────────────────────────────
# Required for OAuth state parameter — Authlib stores the state in the session
# to prevent CSRF attacks during the OAuth redirect flow.
# Session cookie must survive Google's redirect back (SameSite=Lax allows top-level GET).
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="joblense_session",
    max_age=86400 * 7,
    same_site="lax",
    https_only=False,
)

# ── CORS Middleware ──────────────────────────────────────
# Required for React frontend to communicate with FastAPI backend.
# allow_credentials=True is CRITICAL — without this, httpOnly cookies
# are blocked by the browser and auth won't work at all.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # Only allow our frontend origin
    allow_credentials=True,   # MUST be True for httpOnly cookie auth to work
    allow_methods=["*"],      # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],      # Allow all headers
)



# ── Include All API Routers ──────────────────────────────
# All routes are versioned under /api/v1 for future API evolution
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(resume_router, prefix="/api/v1/resume", tags=["Resume"])
app.include_router(ats_router, prefix="/api/v1/ats", tags=["ATS Analysis"])
app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["Job Applications"])
app.include_router(
    recommendations_router,
    prefix="/api/v1/recommendations",
    tags=["Recommendations"],
)


# ── Global Exception Handler ────────────────────────────
# Catches any unhandled exception and returns a clean JSON response.
# Never exposes SQL errors, stack traces, or internal details to the client.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Something went wrong. Please try again.",
            "data": None,
        },
    )


# ── Startup Event ────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    """
    Runs once when the server starts.
    - Creates SQL tables if they don't exist (SQLite dev mode)
    - Creates upload directory for resume files
    - Starts APScheduler for cron jobs (interview reminders)
    - Creates MongoDB indexes for query performance
    """
    # Ensure required environment variables are present
    missing_settings = get_missing_required_settings()
    if missing_settings:
        missing = ", ".join(missing_settings)
        logger.error(f"Missing required environment variables: {missing}")
        raise RuntimeError(
            f"Missing required environment variables: {missing}. "
            "Check backend/.env and restart the server."
        )

    # Create SQL tables (safe for SQLite dev — no-op if tables exist)
    try:
        await create_tables()
        logger.info("Database tables ready")
    except Exception as error:
        logger.error(f"Failed to create tables: {error}")

    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(f"Upload directory: {os.path.abspath(settings.UPLOAD_DIR)}")

    # Start the cron job scheduler
    try:
        start_scheduler()
        logger.info("APScheduler started — interview reminders active")
    except Exception as error:
        logger.error(f"Failed to start scheduler: {error}")

    # Create MongoDB performance indexes (optional — app works without MongoDB)
    try:
        if create_mongodb_indexes:
            await create_mongodb_indexes()
            logger.info("MongoDB indexes created")
    except Exception as error:
        logger.warning(f"MongoDB not available (non-fatal): {error}")


# ── Shutdown Event ───────────────────────────────────────
@app.on_event("shutdown")
async def on_shutdown():
    """
    Runs when the server is shutting down.
    Gracefully stops the scheduler.
    """
    stop_scheduler()
    logger.info("JobLense API shutdown complete")


# ── Health Check Endpoint ────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check — returns ok if the server is running."""
    return {"status": "ok", "service": "JobLense API"}


# ── Root Redirect ────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint — directs to API documentation."""
    return {
        "message": "Welcome to JobLense API",
        "docs": "/docs",
        "health": "/health",
    }
