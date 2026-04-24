"""
VoteWise AI — FastAPI Application Entry Point
Configures middleware, lifespan events, and routes.
"""

import os
import time
import uuid
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.api.router import api_router
from app.middleware.pii_middleware import PIIRedactionMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.models.database import get_database, close_database
from app.core.cache import seed_faqs

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limiter import limiter

from app.core.logging import setup_cloud_logging

# Configure Cloud Logging for GCP
setup_cloud_logging()
logger = logging.getLogger("votewise")

# Performance & Observability: GCP Cloud Trace & Profiler
try:
    from google.cloud import profiler
    from google.cloud import trace_v2
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project_id:
        # Start Profiler
        profiler.start(service="votewise-ai", service_version="1.0.0", verbose=1)
        logger.info("✅ GCP Cloud Profiler initialized")
except ImportError:
    logger.info("ℹ️ GCP Profiler/Trace not installed, skipping")
except Exception as e:
    logger.warning(f"⚠️ Could not initialize GCP services: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager — startup and shutdown events."""
    settings = get_settings()

    # --- Startup ---
    logger.info("🗳️  Starting VoteWise AI v%s", settings.APP_VERSION)

    # Initialize database
    db = await get_database(settings.DATABASE_PATH)
    logger.info("✅ Database initialized: %s", settings.DATABASE_PATH)

    # Seed FAQ cache
    faq_path = Path(__file__).parent.parent / "data" / "faq_seed.json"
    if faq_path.exists():
        with open(faq_path, "r", encoding="utf-8") as f:
            faqs = json.load(f)
        count = await seed_faqs(faqs, settings.DATABASE_PATH)
        logger.info("✅ Seeded %d FAQ entries", count)
    else:
        logger.warning("⚠️  FAQ seed file not found: %s", faq_path)

    # Check Gemini API key
    if settings.GEMINI_API_KEY:
        logger.info("✅ Gemini API key configured")
    else:
        logger.warning("⚠️  GEMINI_API_KEY not set — AI features will use fallback responses")

    logger.info("🚀 VoteWise AI is ready!")

    yield

    # --- Shutdown ---
    logger.info("Shutting down VoteWise AI...")
    await close_database()
    logger.info("👋 Goodbye!")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "An AI-powered Election Process Education Assistant that helps "
            "Indian citizens understand voter registration, EVM/VVPAT usage, "
            "and find factual candidate information."
        ),
        lifespan=lifespan,
    )

    # --- Middleware (order matters: last added = first executed) ---

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)

    # PII Redaction
    app.add_middleware(PIIRedactionMiddleware)

    # Rate Limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Gzip Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # --- Routes ---
    app.include_router(api_router)

    # --- Static Files & SPA Support ---
    static_path = Path(__file__).parent.parent / "static"
    
    if static_path.exists():
        app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
        
        # Fallback for SPA routing: serve index.html for any unknown route
        @app.exception_handler(404)
        async def spa_fallback(request, exc):
            if not request.url.path.startswith("/api"):
                return FileResponse(static_path / "index.html")
            return JSONResponse({"detail": "Not Found"}, status_code=404)
    else:
        @app.get("/")
        async def root():
            return {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "docs": "/docs",
                "health": "/api/health",
                "message": "Build frontend and place in backend/static to see the UI here."
            }

    return app


# Create the app instance
app = create_app()
