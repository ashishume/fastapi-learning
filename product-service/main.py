"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import Base, engine
from api.endpoints import items
from api.endpoints import categories
from core.middleware import AuthMiddleware
from core.utils import auth_guard
from core.redis_client import connect_redis, close_redis
from core.rate_limiter import add_rate_limit_headers
from core.rate_limit_config import RateLimitConfig
import models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    This replaces the deprecated @app.on_event decorators.
    """
    # Startup
    logger.info("Starting up application...")
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

    # Connect to Redis for caching and rate limiting
    await connect_redis()
    logger.info(f"Rate limiting enabled: {RateLimitConfig.ENABLED}")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    logger.info("Closing database connections...")
    engine.dispose()
    
    await close_redis()
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Product Service",
    description="A product service for the application",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Rate Limiting Middleware =====
# Add rate limit headers to all responses
# This middleware adds X-RateLimit-* headers to inform clients about their rate limit status
app.middleware("http")(add_rate_limit_headers)


# auth guard for all routes
# app.add_middleware(AuthMiddleware)


# Include routers
app.include_router(
    items.router,
    prefix="/product/items",
    tags=["items"],
    # auth guard for all routes inside the items router
    dependencies=[Depends(auth_guard)],
)
app.include_router(
    categories.router,
    prefix="/product/categories",
    tags=["categories"],
    dependencies=[Depends(auth_guard)],
)


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint to check if the API is running.

    Returns:
        dict: Welcome message and API status
    """
    return {
        "message": "Welcome to product service",
        "status": "running",
        "docs": "/docs",
    }
