"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models
from api.v1.routes import documents
from core.utils import auth_guard
from api.v1.routes import workspaces


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
    # logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

    # Connect to Redis for caching and rate limiting
    # await connect_redis()

    # Initialize Elasticsearch client
    # logger.info("Initializing Elasticsearch client...")
    yield

    # Shutdown
    # logger.info("Shutting down application...")
    logger.info("Closing database connections...")
    engine.dispose()
    # logger.info("Closing Redis connection...")
    # await close_redis()
    # logger.info("Closing Elasticsearch client...")
    # close_elasticsearch_client()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Document Service",
    description="Document Service for the document management system",
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
routes = [
    (documents.router, "/documents", ["documents"], []),
    (workspaces.router, "/workspaces", ["workspaces"], []),
]

for router, prefix, tags, dependencies in routes:
    app.include_router(router, prefix=prefix, tags=tags, dependencies=dependencies)


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to Document Service",
        "status": "running",
        "docs": "/docs",
    }
