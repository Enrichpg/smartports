# SmartPort Backend - Main FastAPI Application
# Entry point for the backend API server

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import os

# Import configuration and routes
from config import settings
from api.health import router as health_router
from api.v1 import router as api_v1_router
from api.routes import realtime  # WebSocket router
from api.routes import admin  # Admin/observability router

# Realtime infrastructure
from realtime.ws_manager import get_manager
from realtime.event_bus import get_event_bus
from cache.redis_service import get_cache, set_cache, RedisCache
from audit.service import AuditService, set_audit_service
from tasks.celery_app import make_celery, set_celery

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize Redis cache
    try:
        cache = RedisCache(settings.redis_url)
        await cache.connect()
        set_cache(cache)
        logger.info("Redis cache initialized")
    except Exception as e:
        logger.warning(f"Redis cache initialization failed: {e}")
    
    # Initialize Celery
    try:
        celery = make_celery(
            broker_url=settings.celery_broker_url,
            result_backend=settings.celery_result_backend,
        )
        set_celery(celery)
        logger.info("Celery worker initialized")
    except Exception as e:
        logger.warning(f"Celery initialization failed: {e}")
    
    # Initialize WebSocket manager
    ws_manager = get_manager()
    logger.info(f"WebSocket manager initialized")
    
    # Initialize event bus
    event_bus = get_event_bus()
    logger.info(f"Event bus initialized")
    
    # TODO: Setup audit service with DB session once DB is initialized
    # This would be done in the database initialization code
    
    logger.info(f"All realtime infrastructure initialized")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")
    
    # Disconnect Redis
    try:
        cache = get_cache()
        if cache:
            await cache.disconnect()
            logger.info("Redis cache disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting Redis: {e}")
    
    logger.info(f"Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS: allow_origins=["*"] is incompatible with allow_credentials=True in browsers.
# In development we allow all via wildcard without credentials; in production set
# CORS_ALLOW_ORIGINS env var to explicit origins (e.g. https://smartport.example.com).
_cors_origins_raw = os.environ.get("CORS_ALLOW_ORIGINS", "")
_cors_origins = (
    [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]
    if _cors_origins_raw
    else ["*"]
)
_allow_credentials = _cors_origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts.split(",")
)

# Include routers
app.include_router(health_router)
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)
app.include_router(realtime.router, prefix=f"{settings.api_v1_prefix}/realtime")
app.include_router(admin.router, prefix=settings.api_v1_prefix)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """SmartPort Operations Center API root endpoint"""
    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "api": f"{settings.api_v1_prefix}/",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
    )
