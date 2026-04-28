# Berth API Routes
# REST endpoints for berth management

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from schemas.berth import (
    BerthResponse,
    BerthListResponse,
    BerthDetailResponse,
    BerthStateChangeRequest,
)
from services.berth_service import berth_service, BerthStateError, BerthConflictError

router = APIRouter(prefix="/berths", tags=["Berths"])


@router.get("", response_model=BerthListResponse, summary="List berths")
async def list_berths(
    port_id: Optional[str] = Query(None, description="Filter by port ID"),
    facility_id: Optional[str] = Query(None, description="Filter by facility ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get berths with optional filtering.
    
    **Query Parameters:**
    - `port_id`: Filter by port ID (all berths in port)
    - `facility_id`: Filter by facility ID (all berths in facility)
    - `limit`, `offset`: Pagination
    
    **Response:** List of Berth entities
    """
    try:
        if facility_id:
            berths, total = await berth_service.get_berths_by_facility(
                facility_id, limit=limit, offset=offset
            )
        elif port_id:
            berths, total = await berth_service.get_berths_by_port(
                port_id, limit=limit, offset=offset
            )
        else:
            raise HTTPException(
                status_code=400, detail="Must specify port_id or facility_id"
            )

        return BerthListResponse(berths=berths, total=total, limit=limit, offset=offset)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch berths: {str(e)}")


@router.get("/{berth_id}", response_model=BerthDetailResponse, summary="Get berth details")
async def get_berth(berth_id: str):
    """
    Get detailed information about a specific berth.
    
    **Parameters:**
    - `berth_id`: Berth URN ID
    
    **Response:** 
    - Berth details
    - Port and facility context
    - Current vessel info if occupied
    - Accommodation capacity
    """
    try:
        berth = await berth_service.get_berth_by_id(berth_id)

        # Enhance with context
        # In production, would fetch port/facility/vessel details
        detail = BerthDetailResponse(
            berth=berth,
            port_name="Port Name",  # Would fetch from Orion
            facility_name="Facility Name",  # Would fetch from Orion
            current_vessel=None if not berth.active_portcall_id else {"status": "occupied"},
        )
        return detail
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Berth not found: {str(e)}")


@router.patch(
    "/{berth_id}/status", response_model=BerthResponse, summary="Change berth status"
)
async def change_berth_status(berth_id: str, request: BerthStateChangeRequest):
    """
    Change berth operational status with state machine validation.
    
    **Valid Transitions:**
    - `free` → `reserved`, `occupied`, `outOfService`
    - `reserved` → `free`, `occupied`, `outOfService`
    - `occupied` → `free`, `outOfService`
    - `outOfService` → `free`
    
    **Request Body:**
    - `new_status`: New status
    - `reason`: Optional reason for change
    - `operator_id`: Operator performing change
    
    **Response:** Updated Berth entity
    """
    try:
        berth = await berth_service.change_berth_status(
            berth_id, request.new_status, reason=request.reason
        )
        return berth
    except BerthStateError as e:
        raise HTTPException(status_code=409, detail=f"Invalid state transition: {str(e)}")
    except BerthConflictError as e:
        raise HTTPException(status_code=409, detail=f"Berth conflict: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to change berth status: {str(e)}"
        )
