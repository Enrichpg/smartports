# Availability API Routes
# REST endpoints for berth availability management

from fastapi import APIRouter, HTTPException, Query
from schemas.availability import (
    AvailabilitySummaryResponse,
    RecalculateAvailabilityRequest,
)
from services.availability_service import availability_service

router = APIRouter(prefix="/availability", tags=["Availability"])


@router.get(
    "/ports/{port_id}",
    response_model=AvailabilitySummaryResponse,
    summary="Get port availability",
)
async def get_port_availability(port_id: str):
    """
    Get availability summary for a port.
    
    **Includes:**
    - Total available berths
    - Availability rate by category
    - Average depth by category
    
    **Parameters:**
    - `port_id`: Port URN ID
    
    **Response:** Availability summary with breakdown by berth category
    """
    try:
        availability = await availability_service.get_port_availability(port_id)
        return availability
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to get availability: {str(e)}")


@router.get(
    "/facilities/{facility_id}",
    response_model=AvailabilitySummaryResponse,
    summary="Get facility availability",
)
async def get_facility_availability(facility_id: str):
    """
    Get availability summary for a specific facility.
    
    **Parameters:**
    - `facility_id`: Facility URN ID
    
    **Response:** Availability summary for facility
    """
    try:
        availability = await availability_service.get_facility_availability(facility_id)
        return availability
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Failed to get facility availability: {str(e)}"
        )


@router.post(
    "/recalculate/{port_id}",
    response_model=AvailabilitySummaryResponse,
    summary="Recalculate port availability",
)
async def recalculate_port_availability(
    port_id: str, request: RecalculateAvailabilityRequest, force: bool = Query(False)
):
    """
    Recalculate and update availability for a port.
    
    **Purpose:**
    - Recomputes available berths from current berth states
    - Updates BoatPlacesAvailable entities in Orion-LD
    - Returns updated availability summary
    
    **Parameters:**
    - `port_id`: Port URN ID
    - `force`: Skip recent cache check
    
    **Response:** Updated availability summary
    """
    try:
        availability = await availability_service.recalculate_port_availability(port_id)
        return availability
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to recalculate availability: {str(e)}"
        )
