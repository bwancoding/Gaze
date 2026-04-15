from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from app.core.database import engine, Base, SessionLocal
from app.routes import events, admin, stakeholders, stakeholder_verify, personas, comments, auth, trending, threads, users, notifications, feedback, analytics
import logging
import os
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models to register them with Base.metadata before table creation
import app.models.trending  # noqa: F401
import app.models.event_analysis  # noqa: F401
import app.models.threads  # noqa: F401
import app.models.user_likes  # noqa: F401
import app.models.notifications  # noqa: F401
import app.models.feedback  # noqa: F401
import app.models.request_log  # noqa: F401
import app.models.page_view  # noqa: F401
import app.models.error_log  # noqa: F401
Base.metadata.create_all(bind=engine)


def _auto_migrate():
    """Auto-apply lightweight additive schema migrations at startup.

    We use this instead of alembic for tiny additive changes so fresh deploys
    on Railway (PostgreSQL) and local dev (SQLite) both pick them up without
    manual steps. Each migration must be idempotent.
    """
    from sqlalchemy import text
    from app.core.database import DATABASE_URL
    is_sqlite = DATABASE_URL.startswith("sqlite")
    try:
        with engine.begin() as conn:
            if is_sqlite:
                cols = conn.execute(text("PRAGMA table_info(trending_events)")).fetchall()
                col_names = {row[1] for row in cols}
                if "timeline_data" not in col_names:
                    conn.execute(text(
                        "ALTER TABLE trending_events ADD COLUMN timeline_data TEXT DEFAULT '[]'"
                    ))
                    logger.info("Auto-migrate: added trending_events.timeline_data (sqlite)")
                if "topic_engagement_score" not in col_names:
                    conn.execute(text(
                        "ALTER TABLE trending_events ADD COLUMN topic_engagement_score FLOAT DEFAULT 0.0"
                    ))
                    logger.info("Auto-migrate: added trending_events.topic_engagement_score (sqlite)")

                ea_cols = conn.execute(text("PRAGMA table_info(event_analyses)")).fetchall()
                ea_col_names = {row[1] for row in ea_cols}
                if "status" not in ea_col_names:
                    conn.execute(text("ALTER TABLE event_analyses ADD COLUMN status VARCHAR(20)"))
                if "last_attempt_at" not in ea_col_names:
                    conn.execute(text("ALTER TABLE event_analyses ADD COLUMN last_attempt_at TIMESTAMP"))
                if "attempt_count" not in ea_col_names:
                    conn.execute(text("ALTER TABLE event_analyses ADD COLUMN attempt_count INTEGER DEFAULT 0"))
                if "error_message" not in ea_col_names:
                    conn.execute(text("ALTER TABLE event_analyses ADD COLUMN error_message TEXT"))
                conn.execute(text(
                    "UPDATE event_analyses SET status = 'done' WHERE status IS NULL AND background IS NOT NULL"
                ))
            else:
                conn.execute(text(
                    "ALTER TABLE trending_events ADD COLUMN IF NOT EXISTS timeline_data JSONB DEFAULT '[]'::jsonb"
                ))
                logger.info("Auto-migrate: ensured trending_events.timeline_data (postgres)")

                conn.execute(text(
                    "ALTER TABLE trending_events ADD COLUMN IF NOT EXISTS topic_engagement_score DOUBLE PRECISION DEFAULT 0.0"
                ))
                logger.info("Auto-migrate: ensured trending_events.topic_engagement_score (postgres)")

                # Widen trending_articles.url from varchar(1000) -> TEXT.
                # Some news feeds ship URLs with huge tracking query strings;
                # the varchar(1000) cap was causing StringDataRightTruncation
                # errors during pipeline ingest. TEXT is effectively unbounded
                # and still supports the UNIQUE constraint.
                url_type = conn.execute(text(
                    "SELECT data_type FROM information_schema.columns "
                    "WHERE table_name = 'trending_articles' AND column_name = 'url'"
                )).scalar()
                if url_type and url_type.lower() != 'text':
                    conn.execute(text(
                        "ALTER TABLE trending_articles ALTER COLUMN url TYPE TEXT"
                    ))
                    logger.info("Auto-migrate: widened trending_articles.url to TEXT (postgres)")

                conn.execute(text("ALTER TABLE event_analyses ADD COLUMN IF NOT EXISTS status VARCHAR(20)"))
                conn.execute(text("ALTER TABLE event_analyses ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMP"))
                conn.execute(text("ALTER TABLE event_analyses ADD COLUMN IF NOT EXISTS attempt_count INTEGER DEFAULT 0"))
                conn.execute(text("ALTER TABLE event_analyses ADD COLUMN IF NOT EXISTS error_message TEXT"))
                conn.execute(text(
                    "UPDATE event_analyses SET status = 'done' WHERE status IS NULL AND background IS NOT NULL"
                ))
                logger.info("Auto-migrate: ensured event_analyses status/attempt columns (postgres)")
    except Exception as e:
        logger.error(f"Auto-migrate failed (non-fatal): {e}")


_auto_migrate()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: start scheduler on startup, cleanup on shutdown"""
    from app.services.scheduler import init_scheduler, shutdown_scheduler
    init_scheduler()
    logger.info("Gaze API started with scheduler")
    yield
    shutdown_scheduler()
    logger.info("Gaze API shut down")


app = FastAPI(
    title="Gaze API",
    description="Multi-perspective News Aggregation Platform API",
    version="0.2.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
)

# Request logging middleware (after CORS so it doesn't interfere)
from app.middleware.request_logger import RequestLoggerMiddleware
app.add_middleware(RequestLoggerMiddleware)

# Register routes
app.include_router(auth.router, tags=["Authentication"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])
app.include_router(stakeholders.router, prefix="/api", tags=["Stakeholders"])
app.include_router(stakeholder_verify.router, prefix="/api", tags=["Verification"])
app.include_router(personas.router, prefix="/api", tags=["Personas"])
app.include_router(comments.router, tags=["Comments"])
app.include_router(trending.router, prefix="/api", tags=["Trending"])
app.include_router(threads.router, prefix="/api", tags=["Threads"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(notifications.router, prefix="/api", tags=["Notifications"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])

# Serve uploaded files
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# Global exception handler - catch unhandled errors and log them
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions, log to DB and return 500."""
    tb = traceback.format_exc()
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if not client_ip and request.client:
        client_ip = request.client.host

    logger.error(
        f"Unhandled exception: {exc}\n"
        f"Method: {request.method} Path: {request.url.path}\n"
        f"Client: {client_ip}\n"
        f"Traceback:\n{tb}"
    )

    # Persist to error_logs table
    try:
        from app.models.error_log import ErrorLog
        db = SessionLocal()
        try:
            error = ErrorLog(
                method=request.method,
                path=str(request.url.path)[:500],
                client_ip=client_ip,
                error_type=type(exc).__name__,
                error_message=str(exc)[:2000],
                traceback=tb[:5000],
            )
            db.add(error)
            db.commit()
        finally:
            db.close()
    except Exception:
        pass  # Don't let error logging cause more errors

    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Optional: Sentry integration (set SENTRY_DSN env var to enable)
_sentry_dsn = os.getenv("SENTRY_DSN")
if _sentry_dsn:
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=_sentry_dsn, traces_sample_rate=0.1)
        logger.info("Sentry error tracking enabled")
    except ImportError:
        logger.warning("SENTRY_DSN set but sentry-sdk not installed. Run: pip install sentry-sdk[fastapi]")


@app.get("/")
async def root():
    return {
        "message": "Gaze API",
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    from datetime import datetime
    return {
        "status": "healthy",
        "version": "0.2.0",
        "timestamp": datetime.utcnow().isoformat()
    }
