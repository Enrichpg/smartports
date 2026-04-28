# Port API Routes
# REST endpoints for port operations

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from schemas.port import PortResponse, PortSummaryResponse, PortListResponse
from services.port_service import port_service

router = APIRouter(prefix="/ports", tags=["Ports"])


@router.get("", response_model=PortListResponse, summary="List all ports")
async def list_ports(
    limit: int = Query(20, ge=1, le=100, description="Max items"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """
    Get all ports in the Galician network.
    
    **Response:**
    - `ports`: List of Port entities
    - `total`: Total number of ports
    - `limit`, `offset`: Pagination info
    """
    try:
        ports, total = await port_service.get_all_ports(limit=limit, offset=offset)
        return PortListResponse(ports=ports, total=total, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ports: {str(e)}")


@router.get("/{port_id}", response_model=PortResponse, summary="Get port details")
async def get_port(port_id: str):
    """
    Get details of a specific port.
    
    **Parameters:**
    - `port_id`: Port URN ID (e.g., urn:smartdatamodels:Port:Galicia:CorA)
    
    **Response:** Port entity with full details
    """
    try:
        port = await port_service.get_port_by_id(port_id)
        return port
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Port not found: {str(e)}")


@router.get("/{port_id}/summary", response_model=PortSummaryResponse, summary="Get port summary")
async def get_port_summary(port_id: str):
    """
    Get operational summary of a port including KPIs.
    
    **Includes:**
    - Berth counts by status
    - Occupancy rate
    - Active vessel count
    - Active alerts count
    
    **Parameters:**
    - `port_id`: Port URN ID
    
    **Response:** Port summary with operational metrics
    """
    try:
        summary = await port_service.get_port_summary(port_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to generate summary: {str(e)}")
