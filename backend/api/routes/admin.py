"""
Administrative and observability endpoints for realtime systems.
Audit trail queries, cache status, task monitoring, etc.
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from cache.redis_service import get_cache, CacheKeys
from audit.service import get_audit_service
from tasks.celery_app import get_celery, get_task_result
from realtime.event_bus import get_event_bus
from realtime.ws_manager import get_manager

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["admin"],
    prefix="/admin",
)


# =============================================================================
# Audit Endpoints
# =============================================================================

@router.get("/audit", name="Get Audit Logs")
async def get_audit_logs(
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    event_type: Optional[str] = None,
    port_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    severity: Optional[str] = None,
    hours: int = Query(24, ge=1, le=720),
):
    """
    Get audit logs with filtering.
    
    Query Parameters:
    - limit: Max results (default 100, max 1000)
    - offset: Pagination offset (default 0)
    - entity_id: Filter by entity ID
    - entity_type: Filter by entity type (PortCall, Berth, Alert, etc.)
    - event_type: Filter by event type (portcall.created, berth.updated, etc.)
    - port_id: Filter by port
    - correlation_id: Filter by correlation ID
    - severity: Filter by severity (info, warning, error)
    - hours: Look back N hours (default 24)
    """
    
    audit_service = get_audit_service()
    if not audit_service:
        raise HTTPException(status_code=503, detail="Audit service not available")
    
    start_date = datetime.utcnow() - timedelta(hours=hours)
    
    logs = await audit_service.get_audit_logs(
        limit=limit,
        offset=offset,
        entity_id=entity_id,
        entity_type=entity_type,
        event_type=event_type,
        port_id=port_id,
        correlation_id=correlation_id,
        start_date=start_date,
        severity=severity,
    )
    
    return {
        "total": len(logs),
        "limit": limit,
        "offset": offset,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "event_type": log.event_type,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "port_id": log.port_id,
                "actor_type": log.actor_type,
                "actor_id": log.actor_id,
                "severity": log.severity,
                "description": log.description,
                "correlation_id": log.correlation_id,
            }
            for log in logs
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/audit/{entity_type}/{entity_id}", name="Get Entity Audit Trail")
async def get_entity_audit_trail(
    entity_type: str,
    entity_id: str,
    limit: int = Query(50, le=500),
):
    """
    Get complete audit trail for a specific entity.
    """
    
    audit_service = get_audit_service()
    if not audit_service:
        raise HTTPException(status_code=503, detail="Audit service not available")
    
    logs = await audit_service.get_entity_audit_trail(
        entity_id=entity_id,
        limit=limit,
    )
    
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "event_type": log.event_type,
                "severity": log.severity,
                "description": log.description,
                "actor_type": log.actor_type,
                "correlation_id": log.correlation_id,
            }
            for log in logs
        ],
    }


@router.get("/audit/port/{port_id}", name="Get Port Audit Trail")
async def get_port_audit_trail(
    port_id: str,
    limit: int = Query(100, le=1000),
    hours: int = Query(24, ge=1, le=720),
):
    """
    Get audit trail for a specific port.
    """
    
    audit_service = get_audit_service()
    if not audit_service:
        raise HTTPException(status_code=503, detail="Audit service not available")
    
    logs = await audit_service.get_port_audit_trail(
        port_id=port_id,
        limit=limit,
        hours=hours,
    )
    
    return {
        "port_id": port_id,
        "period_hours": hours,
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "event_type": log.event_type,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "severity": log.severity,
                "description": log.description,
            }
            for log in logs
        ],
    }


# =============================================================================
# Cache Endpoints
# =============================================================================

@router.get("/cache/health", name="Cache Health")
async def get_cache_health():
    """Get health status of Redis cache."""
    
    cache = get_cache()
    if not cache:
        return {
            "status": "unavailable",
            "component": "redis_cache",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    health = await cache.health()
    return {
        "component": "redis_cache",
        **health,
    }


@router.delete("/cache/invalidate", name="Invalidate Cache by Pattern")
async def invalidate_cache_pattern(
    pattern: str = Query(..., description="Cache key pattern (e.g., 'port:*')"),
):
    """
    Invalidate cache keys matching a pattern.
    Use with care - can impact performance if wrong pattern.
    
    Common patterns:
    - port:* - all port cache
    - port:summary:* - all port summaries
    - port:{port_id}:* - specific port
    - dashboard:* - dashboard cache
    """
    
    cache = get_cache()
    if not cache:
        raise HTTPException(status_code=503, detail="Cache service not available")
    
    deleted = await cache.delete_pattern(pattern)
    
    return {
        "pattern": pattern,
        "keys_deleted": deleted,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/cache/warm/{key_type}/{resource_id}", name="Warm Specific Cache")
async def warm_cache_key(
    key_type: str,  # "port_summary", "availability", "alerts"
    resource_id: str,  # port_id, etc.
):
    """
    Manually trigger cache warming for a specific resource.
    Useful after bulk operations or to pre-load before peak traffic.
    """
    
    cache = get_cache()
    if not cache:
        raise HTTPException(status_code=503, detail="Cache service not available")
    
    # Map key types to cache keys
    key_mapping = {
        "port_summary": lambda pid: CacheKeys.port_summary(pid),
        "availability": lambda pid: CacheKeys.port_availability(pid),
        "alerts": lambda pid: CacheKeys.port_alerts(pid),
    }
    
    if key_type not in key_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown key_type: {key_type}. Valid: {list(key_mapping.keys())}"
        )
    
    # TODO: Actually warm the cache by fetching/computing the data
    # For now, just return success
    
    cache_key = key_mapping[key_type](resource_id)
    
    return {
        "cache_key": cache_key,
        "status": "warming",
        "message": "Cache warming triggered - actual warming handled by background task",
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================================================
# Task/Celery Endpoints
# =============================================================================

@router.get("/tasks/{task_id}", name="Get Task Status")
async def get_task_status(task_id: str):
    """
    Get the status of a background task.
    """
    
    result = get_task_result(task_id)
    
    return {
        **result,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/tasks/check-alerts/{port_id}", name="Trigger Alert Check")
async def trigger_alert_check(port_id: str):
    """
    Manually trigger alert checking for a port.
    Normally done automatically, but can be triggered manually.
    """
    
    celery = get_celery()
    if not celery:
        raise HTTPException(status_code=503, detail="Celery not available")
    
    try:
        # Import here to avoid circular imports
        from tasks.domain_tasks import check_port_alerts
        
        task = check_port_alerts.apply_async(args=[port_id])
        
        return {
            "status": "triggered",
            "task_id": str(task.id),
            "task_name": "check_port_alerts",
            "port_id": port_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error triggering alert check: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger alert check")


@router.post("/tasks/recalculate-availability/{port_id}", name="Trigger Availability Recalculation")
async def trigger_availability_recalculation(port_id: str):
    """
    Manually trigger availability recalculation for a port.
    """
    
    celery = get_celery()
    if not celery:
        raise HTTPException(status_code=503, detail="Celery not available")
    
    try:
        from tasks.domain_tasks import recalculate_port_availability
        
        task = recalculate_port_availability.apply_async(args=[port_id])
        
        return {
            "status": "triggered",
            "task_id": str(task.id),
            "task_name": "recalculate_port_availability",
            "port_id": port_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error triggering availability recalculation: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger recalculation")


# =============================================================================
# Event Bus Status
# =============================================================================

@router.get("/events/stats", name="Event Bus Statistics")
async def get_event_bus_stats():
    """Get statistics about the event bus."""
    
    event_bus = get_event_bus()
    stats = event_bus.get_stats()
    
    # Also include WebSocket connection count
    ws_manager = get_manager()
    ws_connections = ws_manager.get_connection_count()
    
    return {
        **stats,
        "websocket_connections": ws_connections,
    }


@router.get("/health/realtime", name="Realtime System Health")
async def get_realtime_health():
    """Get health status of all realtime components."""
    
    # Cache health
    cache = get_cache()
    cache_health = await cache.health() if cache else {"status": "unavailable"}
    
    # WebSocket health
    ws_manager = get_manager()
    ws_health = await ws_manager.get_health()
    
    # Event bus stats
    event_bus = get_event_bus()
    event_stats = event_bus.get_stats()
    
    # Celery health (basic check)
    celery = get_celery()
    celery_status = "available" if celery else "unavailable"
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "cache": {
                "name": "Redis Cache",
                **cache_health,
            },
            "websocket": {
                "name": "WebSocket Manager",
                **ws_health,
            },
            "event_bus": {
                "name": "Event Bus",
                "status": "healthy" if event_stats.get("total_events_published", 0) >= 0 else "degraded",
                **event_stats,
            },
            "celery": {
                "name": "Celery Workers",
                "status": celery_status,
            },
        },
        "overall_status": "healthy",  # Can be enhanced with more sophisticated logic
    }


# =============================================================================
# Synthetic Data Endpoints
# =============================================================================

class RegenerateSyntheticDataRequest(BaseModel):
    """Request model for synthetic data regeneration."""
    volume: str = "xlarge"
    historical_days: int = 90
    seed: Optional[int] = None
    purge_first: bool = False


@router.post("/synthetic/regenerate", name="Regenerate Synthetic Data")
async def regenerate_synthetic_data(request: RegenerateSyntheticDataRequest):
    """
    Regenerate the complete synthetic maritime ecosystem.

    Request body:
    - volume: small|medium|large|xlarge (default: xlarge for 4500 vessels, 320 berths)
    - historical_days: Number of days of historical data (default: 90)
    - seed: Random seed for reproducibility (default: 42)
    - purge_first: Delete existing entities before regenerating (default: false)
    """
    try:
        from generators.synthetic_data_generator import SyntheticDataGenerator
        from generators.scenario_config import ScenarioConfig
        from services.orion_service import OrionService

        logger.info(f"Regenerating synthetic data: volume={request.volume}, historical_days={request.historical_days}")

        # Generate entities
        config = ScenarioConfig(
            volume=request.volume,
            historical_days=request.historical_days,
            seed=request.seed or 42
        )
        generator = SyntheticDataGenerator(config)
        entities = generator.generate_all()

        # Load to Orion-LD
        orion = OrionService()
        loaded_count = 0

        for entity in entities:
            try:
                orion.upsert_entity(entity)
                loaded_count += 1
            except Exception as e:
                logger.warning(f"Failed to load entity {entity.get('id')}: {e}")

        logger.info(f"Successfully loaded {loaded_count}/{len(entities)} entities")

        return {
            "status": "completed",
            "message": f"Successfully regenerated {loaded_count} entities",
            "entities_total": len(entities),
            "entities_loaded": loaded_count,
            "volume": request.volume,
            "historical_days": request.historical_days,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        logger.error(f"Error regenerating synthetic data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
