# API v1 Routes - SmartPort Domain Business API
# Main router for domain operations: ports, berths, availability, vessels, PortCalls, alerts

from fastapi import APIRouter
from datetime import datetime
from api.routes import ports, berths, availability, vessels, portcalls, alerts

router = APIRouter()

# Include domain routers
router.include_router(ports.router)
router.include_router(berths.router)
router.include_router(availability.router)
router.include_router(vessels.router)
router.include_router(portcalls.router)
router.include_router(alerts.router)


# Root endpoint
@router.get("/", name="API v1 Root")
async def api_v1_root():
    """SmartPort API v1 root - Domain operations API"""
    return {
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "api_type": "Domain Business API",
        "description": "Real-time port operations including berth management, availability, vessel authorization, port calls, and alerts",
        "domain_areas": {
            "ports": "Port management and operational summaries",
            "berths": "Berth status and allocation",
            "availability": "Berth availability by category",
            "vessels": "Vessel registry and authorizations",
            "portcalls": "Port call lifecycle management",
            "alerts": "Operational alerts and monitoring",
        },
        "endpoints": {
            "ports": "/ports",
            "berths": "/berths",
            "availability": "/availability",
            "vessels": "/vessels",
            "portcalls": "/portcalls",
            "alerts": "/alerts",
        }
    }

@router.get("/sources/status", name="Data Sources Status")
async def get_sources_status():
    """
    Get status of all real data sources and fallback simulators.
    Shows what data is coming from where.
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sources": {
            "AEMET": {
                "type": "real",
                "status": "enabled" if settings.aemet_api_key else "disabled",
                "description": "Spanish meteorological service",
                "update_frequency": f"{settings.weather_update_frequency}s",
                "entities": ["WeatherObserved"],
                "regions": ["Galicia"],
            },
            "MeteoGalicia": {
                "type": "real",
                "status": "enabled" if settings.enable_real_data_ingestion else "disabled",
                "description": "Galician meteorological and oceanographic data",
                "update_frequency": f"{settings.weather_update_frequency}s",
                "entities": ["WeatherObserved", "SeaConditionObserved"],
                "regions": ["Galicia"],
            },
            "PuertosDelEstado": {
                "type": "real",
                "status": "enabled" if settings.enable_real_data_ingestion else "disabled",
                "description": "Spain's Port Authority sea conditions",
                "update_frequency": f"{settings.ocean_conditions_update_frequency}s",
                "entities": ["SeaConditionObserved"],
                "regions": ["Galician Ports"],
            },
            "Simulators": {
                "type": "synthetic",
                "status": "enabled" if settings.enable_fallback_simulators else "disabled",
                "description": "Realistic simulated operational data (fallback)",
                "update_frequency": "variable",
                "entities": ["Berth", "BoatPlacesAvailable", "Vessel", "AirQualityObserved"],
                "regions": ["All Ports"],
                "note": "Used when real APIs unavailable or insufficient granularity"
            }
        },
        "configuration": {
            "real_data_enabled": settings.enable_real_data_ingestion,
            "fallback_simulators_enabled": settings.enable_fallback_simulators,
            "orion_base_url": settings.orion_base_url,
            "quantumleap_base_url": settings.quantumleap_base_url,
        }
    }


# ============================================================================
# PORTS - List and Basic Info
# ============================================================================

@router.get("/ports", name="List Ports")
async def get_ports():
    """List all Galician ports with basic operational data"""
    
    # Galician ports
    ports = [
        {"id": "80003", "name": "Vigo", "region": "Rias Bajas"},
        {"id": "80002", "name": "Pontevedra", "region": "Rias Bajas"},
        {"id": "80001", "name": "Ferrol", "region": "Rias Altas"},
        {"id": "80004", "name": "Coruña", "region": "Atlantic"},
        {"id": "80005", "name": "Lugo", "region": "Rias Altas"},
    ]
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_ports": len(ports),
        "ports": ports,
        "data_source": "seed",
    }


@router.get("/ports/{port_id}", name="Get Port Details")
async def get_port_details(port_id: str):
    """Get detailed information about a specific port"""
    
    try:
        # Query Orion for Port entity
        entities = await orion_service.query_entities(
            entity_type="Port",
            query_filter=f"id=urn:ngsi-ld:Port:{port_id}"
        )
        
        if entities:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "port": entities[0],
            }
        else:
            raise HTTPException(status_code=404, detail=f"Port {port_id} not found")
    
    except Exception as e:
        logger.error(f"Error fetching port {port_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# LIVE DATA - Real-time Observations
# ============================================================================

@router.get("/ports/{port_id}/live/weather", name="Port Weather Live")
async def get_port_weather_live(port_id: str):
    """
    Get current weather observations for a port.
    Data source: AEMET (real) or MeteoGalicia (real) or simulated if unavailable.
    """
    
    try:
        # Query Orion for latest WeatherObserved entities for this port
        entities = await orion_service.query_entities(
            entity_type="WeatherObserved",
            query_filter=f"refPort.object=urn:ngsi-ld:Port:{port_id}"
        )
        
        if not entities:
            return {
                "status": "no_data",
                "port_id": port_id,
                "message": "No weather data available for this port",
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        # Return most recent observation
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
        logger.error(f"Error fetching weather for {port_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ports/{port_id}/live/ocean", name="Port Ocean Conditions Live")
async def get_port_ocean_live(port_id: str):
    """
    Get current oceanographic/sea conditions for a port.
    Data source: Puertos del Estado (real) or simulated.
    """
    
    try:
        entities = await orion_service.query_entities(
            entity_type="SeaConditionObserved",
            query_filter=f"refPort.object=urn:ngsi-ld:Port:{port_id}"
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
        logger.error(f"Error fetching ocean conditions for {port_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ports/{port_id}/live/operations", name="Port Operations Live")
async def get_port_operations_live(port_id: str):
    """
    Get current operational data for a port.
    Includes: berth status, boat places availability, active vessels.
    Data source: Simulators (realistic operational data not directly available via APIs).
    """
    
    try:
        berths = await orion_service.query_entities(
            entity_type="Berth",
            query_filter=f"port.object=urn:ngsi-ld:Port:{port_id}"
        )
        
        places = await orion_service.query_entities(
            entity_type="BoatPlacesAvailable",
            query_filter=f"refPort.object=urn:ngsi-ld:Port:{port_id}"
        )
        
        vessels = await orion_service.query_entities(
            entity_type="Vessel",
            query_filter=f"atPort.object=urn:ngsi-ld:Port:{port_id}"
        )
        
        return {
            "port_id": port_id,
            "timestamp": datetime.utcnow().isoformat(),
            "operational_status": {
                "berths": {
                    "total": len(berths),
                    "occupied": sum(1 for b in berths if b.get("occupied", {}).get("value")),
                    "data": berths[:5]  # Return first 5 for brevity
                },
                "boat_places": places,
                "vessels_present": {
                    "count": len(vessels),
                    "data": vessels[:10]  # Return first 10
                }
            },
            "data_source": "mixed (simulators)",
        }
    
    except Exception as e:
        logger.error(f"Error fetching operations for {port_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HISTORICAL DATA - Time Series
# ============================================================================

@router.get("/ports/{port_id}/history/weather", name="Port Weather History")
async def get_port_weather_history(
    port_id: str,
    hours: int = Query(24, ge=1, le=730)  # Default 24 hours, max 30 days
):
    """
    Get historical weather data for a port from QuantumLeap.
    
    Args:
        port_id: Port identifier
        hours: Number of hours of history (1-730)
    """
    
    try:
        # Query QuantumLeap for time series data
        # This would require QuantumLeap client integration
        
        return {
            "port_id": port_id,
            "hours_requested": hours,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "not_implemented_yet",
            "message": "Historical weather data integration with QuantumLeap pending",
            "note": "Will provide temperature, humidity, pressure, wind trends over time"
        }
    
    except Exception as e:
        logger.error(f"Error fetching weather history for {port_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ports/{port_id}/history/availability", name="Port Availability History")
async def get_port_availability_history(
    port_id: str,
    hours: int = Query(7*24, ge=1, le=90*24)  # Default 7 days
):
    """
    Get historical berth availability and occupancy trends.
    
    Args:
        port_id: Port identifier
        hours: Number of hours of history
    """
    
    return {
        "port_id": port_id,
        "hours_requested": hours,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "not_implemented_yet",
        "message": "Historical availability data from QuantumLeap pending",
        "note": "Will show occupancy trends, dwell times, availability patterns"
    }


# ============================================================================
# BERTHS
# ============================================================================

@router.get("/berths", name="List All Berths")
async def get_all_berths():
    """List all berths across all ports"""
    
    try:
        berths = await orion_service.query_entities(entity_type="Berth")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_berths": len(berths),
            "berths": berths[:50],  # Return first 50 for API response size
            "data_source": "Orion-LD"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# VESSELS
# ============================================================================

@router.get("/vessels", name="List All Vessels")
async def get_all_vessels():
    """List all active vessels in the system"""
    
    try:
        vessels = await orion_service.query_entities(entity_type="Vessel")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_vessels": len(vessels),
            "vessels": vessels[:50],
            "data_source": "Orion-LD (mixed real/simulated)"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
