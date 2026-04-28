# PortCall API Routes
# REST endpoints for port call lifecycle management

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from schemas.portcall import (
    PortCallResponse,
    PortCallListResponse,
    PortCallCreateRequest,
    PortCallStatusChangeRequest,
    PortCallCloseRequest,
)
from services.portcall_service import portcall_service, PortCallError

router = APIRouter(prefix="/portcalls", tags=["PortCalls"])


@router.get("", response_model=PortCallListResponse, summary="List PortCalls")
async def list_portcalls(
    port_id: Optional[str] = Query(None, description="Filter by port ID"),
    active_only: bool = Query(False, description="Only active PortCalls"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get PortCalls with optional filtering.
    
    **Query Parameters:**
    - `port_id`: Filter by port
    - `active_only`: Only show active visits
    - `limit`, `offset`: Pagination
    
    **Response:** List of PortCall entities
    """
    try:
        if port_id:
            if active_only:
                portcalls = await portcall_service.get_active_portcalls(port_id=port_id)
                total = len(portcalls)
                portcalls_data = portcalls[offset : offset + limit]
            else:
                portcalls_data, total = await portcall_service.get_portcalls_by_port(
                    port_id, limit=limit, offset=offset
                )
        else:
            if active_only:
                portcalls = await portcall_service.get_active_portcalls()
                total = len(portcalls)
                portcalls_data = portcalls[offset : offset + limit]
            else:
                portcalls_data, total = await portcall_service.get_all_portcalls(
                    limit=limit, offset=offset
                )

        return PortCallListResponse(
            portcalls=portcalls_data, total=total, limit=limit, offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch PortCalls: {str(e)}")


@router.get("/{portcall_id}", response_model=PortCallResponse, summary="Get PortCall details")
async def get_portcall(portcall_id: str):
    """
    Get detailed information about a specific PortCall.
    
    **Parameters:**
    - `portcall_id`: PortCall URN ID
    
    **Response:** PortCall entity with full lifecycle information
    """
    try:
        portcall = await portcall_service.get_portcall_by_id(portcall_id)
        return portcall
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"PortCall not found: {str(e)}")


@router.post("", response_model=PortCallResponse, summary="Create PortCall", status_code=201)
async def create_portcall(request: PortCallCreateRequest):
    """
    Create a new PortCall (vessel visit).
    
    **Validations:**
    - Vessel must be authorized
    - Insurance must be valid (if required)
    - If berth specified, must be available
    
    **Request Body:**
    - `vessel_id`: Vessel URN ID
    - `port_id`: Port URN ID
    - `estimated_arrival`: Expected arrival time
    - `estimated_departure`: Expected departure time (optional)
    - `berth_id`: Optional berth assignment
    - `purpose`: Visit purpose (load, unload, repair, etc.)
    - `cargo_type`: Cargo type if relevant
    
    **Response:** Created PortCall entity with ID
    """
    try:
        portcall = await portcall_service.create_portcall(
            vessel_id=request.vessel_id,
            port_id=request.port_id,
            estimated_arrival=request.estimated_arrival,
            estimated_departure=request.estimated_departure,
            berth_id=request.berth_id,
            purpose=request.purpose,
            cargo_type=request.cargo_type,
        )
        return portcall
    except PortCallError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create PortCall: {str(e)}")


@router.patch(
    "/{portcall_id}/status", response_model=PortCallResponse, summary="Change PortCall status"
)
async def change_portcall_status(portcall_id: str, request: PortCallStatusChangeRequest):
    """
    Change PortCall status with state machine validation.
    
    **Valid Transitions:**
    - `scheduled` → `expected`, `cancelled`
    - `expected` → `active`, `cancelled`
    - `active` → `completed`, `cancelled`
    - `completed` → (terminal)
    - `cancelled` → (terminal)
    
    **Request Body:**
    - `new_status`: New status
    - `reason`: Optional reason for change
    - `operator_id`: Operator performing change
    
    **Response:** Updated PortCall entity
    """
    try:
        portcall = await portcall_service.change_portcall_status(
            portcall_id, request.new_status, reason=request.reason
        )
        return portcall
    except PortCallError as e:
        raise HTTPException(status_code=409, detail=f"Status change failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change status: {str(e)}")


@router.post("/{portcall_id}/close", response_model=PortCallResponse, summary="Close PortCall")
async def close_portcall(portcall_id: str, request: PortCallCloseRequest):
    """
    Close a PortCall (mark as completed and free berth).
    
    **Purpose:**
    - Transitions to COMPLETED status
    - Records actual departure time
    - Frees assigned berth
    
    **Request Body:**
    - `actual_departure`: Actual departure timestamp
    - `notes`: Optional closing notes
    - `operator_id`: Operator closing the visit
    
    **Response:** Completed PortCall entity
    """
    try:
        portcall = await portcall_service.close_portcall(
            portcall_id, request.actual_departure, notes=request.notes
        )
        return portcall
    except PortCallError as e:
        raise HTTPException(status_code=409, detail=f"Close failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close PortCall: {str(e)}")
