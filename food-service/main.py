"""Main FastAPI application entry point."""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from core.utils import auth_guard
from database import Base, engine
import models
from api.v1.routes import categories, restaurants
from api.v1.routes import foods
from api.v1.routes import orders
from api.v1.routes import menu
from api.v1.routes import web_server

from core.redis_client import connect_redis, close_redis

# Import sharding module (optional - enable with ENABLE_SHARDING=true)
ENABLE_SHARDING = os.getenv("ENABLE_SHARDING", "false").lower() == "true"

if ENABLE_SHARDING:
    from core.db_sharding import (
        get_shard_manager,
        create_tables_on_all_shards,
    )

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

    await connect_redis()
    
    if ENABLE_SHARDING:
        # Sharded database setup
        logger.info("Sharding enabled - initializing shards...")
        shard_manager = get_shard_manager()
        logger.info(f"Configured {shard_manager.num_shards} database shard(s)")
        
        # Create tables on all shards
        create_tables_on_all_shards(Base)
        logger.info("Database tables created on all shards")
        
        # Health check
        health = shard_manager.health_check()
        for shard_id, is_healthy in health.items():
            status = "healthy" if is_healthy else "unhealthy"
            logger.info(f"Shard {shard_id}: {status}")
    else:
        # Standard single database setup
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    
    if ENABLE_SHARDING:
        logger.info("Disposing all shard connections...")
        shard_manager = get_shard_manager()
        shard_manager.dispose_all()
    else:
        logger.info("Closing database connections...")
        engine.dispose()
    
    logger.info("Application shutdown complete")

    await close_redis()


# Create FastAPI application
app = FastAPI(
    title="Food Service",
    description="Food Service for the food management system",
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
    (categories.router, "/categories", ["categories"], [Depends(auth_guard)]),
    (restaurants.router, "/restaurants", ["restaurants"], [Depends(auth_guard)]),
    (foods.router, "/foods", ["foods"], [Depends(auth_guard)]),
    (orders.router, "/orders", ["orders"], [Depends(auth_guard)]),
    (menu.router, "/menu", ["menu"], [Depends(auth_guard)]),
    (web_server.router, "/ws", ["ws"], []),
]

for router, prefix, tags, dependencies in routes:
    app.include_router(router, prefix=prefix, tags=tags, 
    dependencies=dependencies
    )


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to Food Service",
        "status": "running",
        "docs": "/docs",
        "sharding_enabled": ENABLE_SHARDING,
    }


@app.get("/health/shards", tags=["health"])
async def shard_health():
    """Check health status of all database shards."""
    if not ENABLE_SHARDING:
        return {
            "sharding_enabled": False,
            "message": "Sharding is not enabled. Set ENABLE_SHARDING=true to enable.",
        }
    
    shard_manager = get_shard_manager()
    health_status = shard_manager.health_check()
    
    return {
        "sharding_enabled": True,
        "total_shards": shard_manager.num_shards,
        "shard_ids": shard_manager.shard_ids,
        "health": {f"shard_{k}": "healthy" if v else "unhealthy" for k, v in health_status.items()},
        "all_healthy": all(health_status.values()),
    }
