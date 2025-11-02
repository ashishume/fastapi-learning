"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import Base, engine
from api.endpoints import items
from api.endpoints import categories
from api.auth import auth
from core.middleware import AuthMiddleware
from core.utils import auth_guard
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

    yield

    # Shutdown
    logger.info("Shutting down application...")
    logger.info("Closing database connections...")
    engine.dispose()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="FastAPI Learning Project",
    description="A learning project for FastAPI with PostgreSQL",
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


# auth guard for all routes
# app.add_middleware(AuthMiddleware)  


# Include routers
app.include_router(
    items.router,
    prefix="/items",
    tags=["items"],
    # auth guard for all routes inside the items router
    dependencies=[Depends(auth_guard)],
)
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint to check if the API is running.

    Returns:
        dict: Welcome message and API status
    """
    return {
        "message": "Welcome to FastAPI Learning Project",
        "status": "running",
        "docs": "/docs",
    }
