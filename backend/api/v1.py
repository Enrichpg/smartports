# API v1 Routes - SmartPort Domain Business API
# Aggregates all domain sub-routers: ports, berths, availability, vessels, portcalls, alerts

from fastapi import APIRouter
from datetime import datetime

from api.routes import ports, berths, availability, vessels, portcalls, alerts
from config import settings

router = APIRouter()

# Include domain sub-routers
router.include_router(ports.router)
router.include_router(berths.router)
router.include_router(availability.router)
router.include_router(vessels.router)
router.include_router(portcalls.router)
router.include_router(alerts.router)


@router.get("/", name="API v1 Root")
async def api_v1_root():
    """SmartPort API v1 root — domain operations overview"""
    return {
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "description": (
            "Real-time port operations: berth management, availability, "
            "vessel authorization, port calls, alerts"
        ),
        "endpoints": {
            "ports": "/api/v1/ports",
            "berths": "/api/v1/berths",
            "availability": "/api/v1/availability",
            "vessels": "/api/v1/vessels",
            "portcalls": "/api/v1/portcalls",
            "alerts": "/api/v1/alerts",
            "realtime_ws": "/api/v1/realtime/ws",
            "admin": "/api/v1/admin",
        },
    }


@router.get("/sources/status", name="Data Sources Status")
async def get_sources_status():
    """Status of all real data sources and fallback simulators."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sources": {
            "AEMET": {
                "type": "real",
                "status": "enabled" if settings.aemet_api_key else "disabled",
                "description": "Spanish meteorological service",
                "update_frequency_s": settings.weather_update_frequency,
                "entities": ["WeatherObserved"],
            },
            "MeteoGalicia": {
                "type": "real",
                "status": "enabled" if settings.enable_real_data_ingestion else "disabled",
                "description": "Galician meteorological and oceanographic data",
                "update_frequency_s": settings.weather_update_frequency,
                "entities": ["WeatherObserved", "SeaConditionObserved"],
            },
            "PuertosDelEstado": {
                "type": "real",
                "status": "enabled" if settings.enable_real_data_ingestion else "disabled",
                "description": "Spain Port Authority sea conditions",
                "update_frequency_s": settings.ocean_conditions_update_frequency,
                "entities": ["SeaConditionObserved"],
            },
            "Simulators": {
                "type": "synthetic",
                "status": "enabled" if settings.enable_fallback_simulators else "disabled",
                "description": "Realistic simulated operational data (fallback)",
                "entities": ["Berth", "BoatPlacesAvailable", "Vessel", "AirQualityObserved"],
                "note": "Active when real APIs are unavailable",
            },
        },
        "configuration": {
            "real_data_enabled": settings.enable_real_data_ingestion,
            "fallback_simulators_enabled": settings.enable_fallback_simulators,
            "orion_base_url": settings.orion_base_url,
            "quantumleap_base_url": settings.quantumleap_base_url,
        },
    }
