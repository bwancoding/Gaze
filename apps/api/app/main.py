from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from app.core.database import engine, Base
from app.routes import events, admin, stakeholders, stakeholder_verify, personas, comments, auth, trending, threads, users, notifications
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models to register them with Base.metadata before table creation
import app.models.trending  # noqa: F401
import app.models.event_analysis  # noqa: F401
import app.models.threads  # noqa: F401
import app.models.user_likes  # noqa: F401
import app.models.notifications  # noqa: F401
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: start scheduler on startup, cleanup on shutdown"""
    from app.services.scheduler import init_scheduler, shutdown_scheduler
    init_scheduler()
    logger.info("WRHITW API started with scheduler")
    yield
    shutdown_scheduler()
    logger.info("WRHITW API shut down")


app = FastAPI(
    title="WRHITW API",
    description="Multi-perspective News Aggregation Platform API",
    version="0.2.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
async def root():
    return {
        "message": "WRHITW API",
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
