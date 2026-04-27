# API Health Check Endpoints
# Provides liveness, readiness, and startup probes for Kubernetes/Docker

from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil

router = APIRouter(tags=["Health"])


@router.get("/health", name="Health Check")
async def health():
    """
    Basic health check endpoint for Docker/Kubernetes probes
    Returns 200 OK if service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/live", name="Liveness Probe")
async def health_live():
    """
    Liveness probe: indicates if application is running
    Used by container orchestrators to restart unhealthy instances
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/ready", name="Readiness Probe")
async def health_ready():
    """
    Readiness probe: indicates if application is ready to accept traffic
    Used by load balancers to route traffic
    """
    try:
        # Add any pre-flight checks here (database connection, etc.)
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "reason": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@router.get("/health/startup", name="Startup Probe")
async def health_startup():
    """
    Startup probe: indicates if application has completed startup
    Used to prevent premature termination
    """
    return {
        "status": "started",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/metrics/system", name="System Metrics")
async def metrics_system():
    """
    Basic system metrics for monitoring
    """
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "timestamp": datetime.utcnow().isoformat(),
    }
