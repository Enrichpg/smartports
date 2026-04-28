# Port API Routes
# REST endpoints for port operations and live data

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from schemas.port import PortResponse, PortSummaryResponse, PortListResponse
from services.port_service import port_service
from services.orion import orion_service

logger = logging.getLogger(__name__)

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

    **Includes:** Berth counts by status, occupancy rate, active vessel count, active alerts count.

    **Parameters:**
    - `port_id`: Port URN ID

    **Response:** Port summary with operational metrics
    """
    try:
        summary = await port_service.get_port_summary(port_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to generate summary: {str(e)}")


# ---------------------------------------------------------------------------
# Live Observation Endpoints (real-time data from Orion-LD)
# ---------------------------------------------------------------------------

@router.get("/{port_id}/live/weather", summary="Port live weather")
async def get_port_weather_live(port_id: str):
    """Current weather observations for a port (AEMET / MeteoGalicia / simulated)."""
    try:
        entities = await orion_service.query_entities(
            entity_type="WeatherObserved",
            q=f"refPort.object==urn:ngsi-ld:Port:{port_id}",
        )
        if not entities:
            return {
                "status": "no_data",
                "port_id": port_id,
                "message": "No weather data available for this port",
                "timestamp": datetime.utcnow().isoformat(),
            }
        latest = entities[0]
        return {
            "port_id": port_id,
            "timestamp": latest.get("dateObserved", {}).get("value"),
            "weather": {
                "temperature": latest.get("temperature", {}).get("value"),
                "humidity": latest.get("relativeHumidity", {}).get("value"),
                "pressure": latest.get("atmosphericPressure", {}).get("value"),
                "wind_speed": latest.get("windSpeed", {}).get("value"),
                "wind_direction": latest.get("windDirection", {}).get("value"),
                "precipitation": latest.get("precipitation", {}).get("value"),
            },
            "source": latest.get("dataProvider", {}).get("value", "unknown"),
            "confidence": latest.get("sourceConfidence", {}).get("value", "N/A"),
        }
    except Exception as e:
        logger.error(f"Error fetching weather for {port_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{port_id}/live/ocean", summary="Port live ocean conditions")
async def get_port_ocean_live(port_id: str):
    """Current oceanographic/sea conditions for a port (Puertos del Estado / simulated)."""
    try:
        entities = await orion_service.query_entities(
            entity_type="SeaConditionObserved",
            q=f"refPort.object==urn:ngsi-ld:Port:{port_id}",
        )
        if not entities:
            return {
                "status": "no_data",
                "port_id": port_id,
                "message": "No ocean condition data available",
                "timestamp": datetime.utcnow().isoformat(),
            }
        latest = entities[0]
        return {
            "port_id": port_id,
            "timestamp": latest.get("dateObserved", {}).get("value"),
            "conditions": {
                "significant_wave_height": latest.get("significantWaveHeight", {}).get("value"),
                "water_temperature": latest.get("waterTemperature", {}).get("value"),
                "wind_speed": latest.get("windSpeed", {}).get("value"),
                "tide_level": latest.get("tideLevel", {}).get("value"),
                "current_speed": latest.get("currentSpeed", {}).get("value"),
            },
            "source": latest.get("dataProvider", {}).get("value", "unknown"),
        }
    except Exception as e:
        logger.error(f"Error fetching ocean conditions for {port_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{port_id}/live/operations", summary="Port live operational data")
async def get_port_operations_live(port_id: str):
    """Current berth status, boat availability, and vessels present at a port."""
    try:
        berths = await orion_service.query_entities(
            entity_type="Berth",
            q=f"port.object==urn:ngsi-ld:Port:{port_id}",
        )
        places = await orion_service.query_entities(
            entity_type="BoatPlacesAvailable",
            q=f"refPort.object==urn:ngsi-ld:Port:{port_id}",
        )
        vessels = await orion_service.query_entities(
            entity_type="Vessel",
            q=f"atPort.object==urn:ngsi-ld:Port:{port_id}",
        )
        return {
            "port_id": port_id,
            "timestamp": datetime.utcnow().isoformat(),
            "operational_status": {
                "berths": {
                    "total": len(berths),
                    "occupied": sum(
                        1 for b in berths
                        if b.get("occupancyStatus", {}).get("value") == "occupied"
                    ),
                    "data": berths[:5],
                },
                "boat_places": places,
                "vessels_present": {"count": len(vessels), "data": vessels[:10]},
            },
            "data_source": "Orion-LD (mixed real/simulated)",
        }
    except Exception as e:
        logger.error(f"Error fetching operations for {port_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Historical Data Endpoints (QuantumLeap/TimescaleDB)
# ---------------------------------------------------------------------------

@router.get("/{port_id}/history/weather", summary="Port weather history")
async def get_port_weather_history(
    port_id: str,
    hours: int = Query(24, ge=1, le=730, description="Hours of history (max 30 days)"),
):
    """Historical weather time-series for a port from QuantumLeap."""
    return {
        "port_id": port_id,
        "hours_requested": hours,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "not_implemented",
        "message": "QuantumLeap historical weather integration pending",
    }


@router.get("/{port_id}/history/availability", summary="Port availability history")
async def get_port_availability_history(
    port_id: str,
    hours: int = Query(168, ge=1, le=2160, description="Hours of history (max 90 days)"),
):
    """Historical berth availability and occupancy trends from QuantumLeap."""
    return {
        "port_id": port_id,
        "hours_requested": hours,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "not_implemented",
        "message": "QuantumLeap historical availability integration pending",
    }
