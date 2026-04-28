# Vessel & Authorization API Routes
# REST endpoints for vessel queries and authorization validation

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from schemas.vessel import VesselResponse, VesselListResponse
from schemas.authorization import (
    AuthorizationResponse,
    AuthorizationValidationRequest,
    AuthorizationValidationResponse,
)
from services.vessel_service import vessel_service
from services.authorization_service import authorization_service

router = APIRouter(tags=["Vessels & Authorizations"])


# Vessel Endpoints
@router.get("/vessels", response_model=VesselListResponse, summary="List vessels")
async def list_vessels(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get all registered vessels.
    
    **Query Parameters:**
    - `limit`: Max items per page
    - `offset`: Pagination offset
    
    **Response:** List of Vessel entities
    """
    try:
        vessels, total = await vessel_service.get_all_vessels(limit=limit, offset=offset)
        return VesselListResponse(vessels=vessels, total=total, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vessels: {str(e)}")


@router.get("/vessels/{vessel_id}", response_model=VesselResponse, summary="Get vessel details")
async def get_vessel(vessel_id: str):
    """
    Get detailed information about a specific vessel.
    
    **Parameters:**
    - `vessel_id`: Vessel URN ID (MasterVessel reference)
    
    **Response:** Vessel entity with specifications
    """
    try:
        vessel = await vessel_service.get_vessel_by_id(vessel_id)
        return vessel
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Vessel not found: {str(e)}")


@router.get("/vessels/imo/{imo_number}", response_model=VesselResponse, summary="Get vessel by IMO")
async def get_vessel_by_imo(imo_number: str):
    """
    Get vessel by IMO number.
    
    **Parameters:**
    - `imo_number`: IMO registration number
    
    **Response:** Vessel entity if found
    """
    try:
        vessel = await vessel_service.get_vessel_by_imo(imo_number)
        return vessel
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Vessel not found: {str(e)}")


# Authorization Endpoints
@router.get(
    "/authorizations/{vessel_id}",
    response_model=AuthorizationResponse,
    summary="Get vessel authorization",
)
async def get_authorization(vessel_id: str, port_id: Optional[str] = Query(None)):
    """
    Get authorization record for a vessel.
    
    **Parameters:**
    - `vessel_id`: Vessel URN ID
    - `port_id`: Optional port ID for port-specific authorization
    
    **Response:** BoatAuthorized entity with authorization details
    """
    try:
        auth = await authorization_service.get_vessel_authorization(vessel_id, port_id=port_id)
        return auth
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Authorization not found: {str(e)}")


@router.post(
    "/authorizations/validate",
    response_model=AuthorizationValidationResponse,
    summary="Validate vessel authorization",
)
async def validate_authorization(request: AuthorizationValidationRequest):
    """
    Validate if a vessel is authorized to operate.
    
    **Validation Checks:**
    - Authorization exists
    - Authorization not expired
    - Authorization not revoked
    - Insurance valid (if requested)
    
    **Request Body:**
    - `vessel_id`: Vessel ID
    - `port_id`: Optional port for port-specific check
    - `check_insurance`: Include insurance validation
    
    **Response:** 
    - `is_authorized`: Boolean result
    - `status`: Authorization status
    - `reason`: Reason if not authorized
    - `details`: Additional information
    """
    try:
        validation = await authorization_service.validate_vessel_authorization(
            vessel_id=request.vessel_id,
            port_id=request.port_id,
            check_insurance=request.check_insurance,
        )
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get(
    "/authorizations",
    response_model=dict,
    summary="List all authorizations",
)
async def list_authorizations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get all vessel authorizations.
    
    **Query Parameters:**
    - `limit`: Max items per page
    - `offset`: Pagination offset
    
    **Response:** List of authorization records
    """
    try:
        authorizations, total = await authorization_service.get_all_authorizations(
            limit=limit, offset=offset
        )
        return {
            "authorizations": authorizations,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch authorizations: {str(e)}")
