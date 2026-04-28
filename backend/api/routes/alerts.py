# Alert API Routes
# REST endpoints for operational alert management

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from schemas.alert import AlertResponse, AlertListResponse, CheckAlertsRequest
from services.alert_service import alert_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertListResponse, summary="List alerts")
async def list_alerts(
    port_id: Optional[str] = Query(None, description="Filter by port"),
    active_only: bool = Query(True, description="Only active alerts"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get alerts with optional filtering.
    
    **Query Parameters:**
    - `port_id`: Filter by port ID
    - `active_only`: Only show active alerts (default: True)
    - `limit`, `offset`: Pagination
    
    **Response:** 
    - `alerts`: List of Alert entities
    - `total`: Total alert count
    - `active`: Count of active alerts
    """
    try:
        if port_id:
            alerts, total = await alert_service.get_port_alerts(
                port_id, active_only=active_only, limit=limit, offset=offset
            )
        else:
            alerts, total = await alert_service.get_all_alerts(
                active_only=active_only, limit=limit, offset=offset
            )

        active_count = sum(1 for a in alerts if a.is_active)
        return AlertListResponse(
            alerts=alerts, total=total, active=active_count, limit=limit, offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")


@router.get("/{alert_id}", response_model=AlertResponse, summary="Get alert details")
async def get_alert(alert_id: str):
    """
    Get detailed information about a specific alert.
    
    **Parameters:**
    - `alert_id`: Alert URN ID
    
    **Response:** Alert entity with full details
    """
    try:
        # In production, would fetch from service
        raise HTTPException(status_code=501, detail="Not yet implemented")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Alert not found: {str(e)}")


@router.post("", response_model=list, summary="Check and generate alerts", status_code=200)
async def check_alerts(request: CheckAlertsRequest):
    """
    Check a port for operational issues and generate alerts.
    
    **Checks Performed:**
    - Vessel authorization validation
    - Occupancy level monitoring
    - Berth assignment conflicts
    
    **Request Body:**
    - `port_id`: Port to check
    - `check_authorizations`: Enable authorization checks (default: True)
    - `check_occupancy`: Enable occupancy checks (default: True)
    - `check_conflicts`: Enable conflict checks (default: True)
    - `severity_threshold`: Minimum severity to report
    
    **Response:** List of generated Alert entities
    """
    try:
        alerts = await alert_service.check_port_alerts(
            port_id=request.port_id,
            check_authorizations=request.check_authorizations,
            check_occupancy=request.check_occupancy,
            check_conflicts=request.check_conflicts,
        )
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert check failed: {str(e)}")


@router.patch(
    "/{alert_id}/acknowledge", response_model=AlertResponse, summary="Acknowledge alert"
)
async def acknowledge_alert(alert_id: str, operator_id: str = Query(...)):
    """
    Acknowledge an alert (mark as seen by operator).
    
    **Parameters:**
    - `alert_id`: Alert URN ID
    - `operator_id`: Operator acknowledging the alert
    
    **Response:** Updated Alert entity with acknowledgement timestamp
    """
    try:
        alert = await alert_service.acknowledge_alert(alert_id, operator_id)
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.patch("/{alert_id}/resolve", response_model=AlertResponse, summary="Resolve alert")
async def resolve_alert(alert_id: str):
    """
    Resolve an alert (mark as addressed).
    
    **Parameters:**
    - `alert_id`: Alert URN ID
    
    **Response:** Updated Alert entity with resolved status
    """
    try:
        alert = await alert_service.resolve_alert(alert_id)
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.get("/ports/{port_id}", response_model=AlertListResponse, summary="Get port alerts")
async def get_port_alerts(
    port_id: str,
    active_only: bool = Query(True),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get all alerts for a specific port.
    
    **Parameters:**
    - `port_id`: Port URN ID
    - `active_only`: Filter to active alerts only
    - `limit`, `offset`: Pagination
    
    **Response:** Port-specific alert list
    """
    try:
        alerts, total = await alert_service.get_port_alerts(
            port_id, active_only=active_only, limit=limit, offset=offset
        )
        active_count = sum(1 for a in alerts if a.is_active)
        return AlertListResponse(
            alerts=alerts, total=total, active=active_count, limit=limit, offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")
