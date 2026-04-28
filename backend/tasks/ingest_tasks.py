# Celery Tasks for Real Data Ingestion
# Periodic tasks for fetching, transforming, and publishing data

import logging
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any

from backend.connectors import AEMETConnector, MeteoGaliciaConnector, PuertosEstadoConnector
from backend.services.transformers import WeatherTransformer, OceanTransformer, AvailabilityTransformer, AirQualityTransformer
from backend.services.orion import OrionService
from backend.simulators import (
    BerthStatusSimulator,
    AvailabilitySimulator,
    VesselSimulator,
    AirQualitySimulator,
)
from backend.tasks.celery import celery_app
from backend.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# WEATHER DATA INGESTION TASKS
# ============================================================================

@celery_app.task(name="ingest_weather_aemet")
def ingest_weather_aemet():
    """
    Fetch weather data from AEMET OpenData API.
    Transform to NGSI-LD and publish to Orion-LD.
    Falls back to simulator if API fails.
    """
    if not settings.enable_real_data_ingestion:
        logger.info("Real data ingestion disabled, skipping AEMET weather")
        return {"status": "skipped"}
    
    logger.info("Starting AEMET weather data ingestion...")
    
    try:
        # Initialize connector
        connector = AEMETConnector(
            api_key=settings.aemet_api_key,
            base_url=settings.aemet_base_url,
        )
        
        # Define Galician locations to monitor
        locations = {
            "Vigo": {"code": "35012", "port": "80003"},
            "Ferrol": {"code": "15023", "port": "80001"},
            "Coruña": {"code": "15001", "port": "80004"},
        }
        
        results = []
        orion = OrionService()
        
        for location_name, location_info in locations.items():
            try:
                # Run async fetch in sync context
                loop = asyncio.get_event_loop()
                weather_data = loop.run_until_complete(
                    connector.get_weather_data(location_info["code"])
                )
                
                if weather_data.get("status") == "success":
                    # Transform to NGSI-LD
                    ngsi_entity = WeatherTransformer.from_aemet(
                        weather_data,
                        location_id=location_info["code"],
                        port_code=location_info["port"]
                    )
                    
                    # Publish to Orion
                    response = orion.update_entity(ngsi_entity)
                    results.append({
                        "location": location_name,
                        "status": "published",
                        "response": response
                    })
                    logger.info(f"AEMET weather published for {location_name}")
                else:
                    logger.warning(f"AEMET failed for {location_name}: {weather_data.get('error')}")
                    results.append({
                        "location": location_name,
                        "status": "failed",
                        "error": weather_data.get("error")
                    })
            
            except Exception as e:
                logger.error(f"Error processing {location_name}: {str(e)}")
                results.append({
                    "location": location_name,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "task": "ingest_weather_aemet",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        }
    
    except Exception as e:
        logger.error(f"AEMET ingestion task failed: {str(e)}")
        return {"task": "ingest_weather_aemet", "status": "failed", "error": str(e)}


@celery_app.task(name="ingest_weather_meteogalicia")
def ingest_weather_meteogalicia():
    """
    Fetch weather data from MeteoGalicia.
    """
    if not settings.enable_real_data_ingestion:
        return {"status": "skipped"}
    
    logger.info("Starting MeteoGalicia weather data ingestion...")
    
    try:
        connector = MeteoGaliciaConnector(
            wms_url=settings.meteogalicia_wms_url,
            wcs_url=settings.meteogalicia_base_url,
        )
        
        # Get coastal observations
        loop = asyncio.get_event_loop()
        coastal_data = loop.run_until_complete(connector.get_coastal_observations())
        
        return {
            "task": "ingest_weather_meteogalicia",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": coastal_data
        }
    
    except Exception as e:
        logger.error(f"MeteoGalicia ingestion failed: {str(e)}")
        return {"task": "ingest_weather_meteogalicia", "status": "failed", "error": str(e)}


# ============================================================================
# OCEAN CONDITIONS INGESTION TASKS
# ============================================================================

@celery_app.task(name="ingest_sea_conditions")
def ingest_sea_conditions():
    """
    Fetch sea conditions from Puertos del Estado.
    Transform to NGSI-LD SeaConditionObserved and publish.
    """
    if not settings.enable_real_data_ingestion:
        return {"status": "skipped"}
    
    logger.info("Starting sea conditions ingestion...")
    
    try:
        connector = PuertosEstadoConnector(base_url=settings.puertos_estado_base_url)
        
        # Galician ports to monitor
        ports = {
            "Vigo": "80003",
            "Pontevedra": "80002",
            "Ferrol": "80001",
            "Coruña": "80004",
        }
        
        results = []
        orion = OrionService()
        
        for port_name, port_code in ports.items():
            try:
                loop = asyncio.get_event_loop()
                sea_data = loop.run_until_complete(
                    connector.get_sea_conditions(port_code)
                )
                
                if sea_data.get("status") == "success":
                    # Transform to NGSI-LD
                    ngsi_entity = OceanTransformer.from_puertos_estado(
                        sea_data,
                        station_id=port_code,
                        port_code=port_code
                    )
                    
                    # Publish to Orion
                    response = orion.update_entity(ngsi_entity)
                    results.append({
                        "port": port_name,
                        "status": "published"
                    })
                
            except Exception as e:
                logger.error(f"Error processing sea conditions for {port_name}: {str(e)}")
        
        return {
            "task": "ingest_sea_conditions",
            "status": "completed",
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Sea conditions ingestion failed: {str(e)}")
        return {"task": "ingest_sea_conditions", "status": "failed", "error": str(e)}


# ============================================================================
# OPERATIONAL DATA INGESTION (SIMULATED)
# ============================================================================

@celery_app.task(name="ingest_berth_status")
def ingest_berth_status():
    """
    Ingest berth status and occupancy.
    Uses simulators as primary source (realistic operational data not directly available).
    Marks data as 'simulator' source for transparency.
    """
    if not settings.enable_fallback_simulators:
        return {"status": "skipped"}
    
    logger.info("Starting berth status ingestion...")
    
    try:
        orion = OrionService()
        results = []
        
        # Galician ports
        ports = ["80003", "80001", "80004", "80002"]
        
        for port_code in ports:
            try:
                simulator = BerthStatusSimulator(port_code=port_code, num_berths=5)
                statuses = simulator.get_all_berth_statuses()
                
                for status in statuses:
                    # Transform to NGSI-LD
                    ngsi_entity = AvailabilityTransformer.berth_status(
                        berth_id=status["berth_id"],
                        port_code=port_code,
                        status=status["status"],
                        occupied=status["occupied"],
                        occupant_vessel_id=status["occupant_vessel_id"],
                        data_source="simulator",
                        confidence=0.3
                    )
                    
                    # Publish to Orion
                    orion.update_entity(ngsi_entity)
                
                results.append({"port": port_code, "berths_updated": len(statuses)})
            
            except Exception as e:
                logger.error(f"Error processing berth status for {port_code}: {str(e)}")
        
        return {
            "task": "ingest_berth_status",
            "status": "completed",
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Berth status ingestion failed: {str(e)}")
        return {"task": "ingest_berth_status", "status": "failed", "error": str(e)}


@celery_app.task(name="ingest_availability")
def ingest_availability():
    """
    Ingest boat places availability.
    Simulated data marked as such.
    """
    if not settings.enable_fallback_simulators:
        return {"status": "skipped"}
    
    logger.info("Starting availability ingestion...")
    
    try:
        orion = OrionService()
        ports = ["80003", "80001", "80004", "80002"]
        
        for port_code in ports:
            try:
                simulator = AvailabilitySimulator(port_code=port_code)
                
                for place_type in ["berth", "mooring", "anchorage"]:
                    availability = simulator.get_available_places(place_type)
                    
                    ngsi_entity = AvailabilityTransformer.boat_places_available(
                        port_code=port_code,
                        port_type=place_type,
                        available_places=availability["available_places"],
                        total_places=availability["total_places"],
                        data_source="simulator"
                    )
                    
                    orion.update_entity(ngsi_entity)
        
        return {"task": "ingest_availability", "status": "completed"}
    
    except Exception as e:
        logger.error(f"Availability ingestion failed: {str(e)}")
        return {"task": "ingest_availability", "status": "failed", "error": str(e)}


@celery_app.task(name="ingest_vessel_data")
def ingest_vessel_data():
    """
    Ingest vessel positions and status.
    Simulated when real AIS data unavailable.
    """
    if not settings.enable_fallback_simulators:
        return {"status": "skipped"}
    
    logger.info("Starting vessel data ingestion...")
    
    try:
        orion = OrionService()
        ports = ["80003", "80001", "80004"]
        
        for port_code in ports:
            try:
                simulator = VesselSimulator(port_code=port_code)
                vessels = simulator.get_all_vessels()
                
                for vessel_data in vessels:
                    ngsi_entity = AvailabilityTransformer.vessel_status(
                        vessel_id=vessel_data["vessel_id"],
                        mmsi=vessel_data["mmsi"],
                        port_code=port_code,
                        status=vessel_data["status"],
                        current_berth=vessel_data["current_berth"],
                        data_source="simulator"
                    )
                    
                    orion.update_entity(ngsi_entity)
        
        return {"task": "ingest_vessel_data", "status": "completed"}
    
    except Exception as e:
        logger.error(f"Vessel data ingestion failed: {str(e)}")
        return {"task": "ingest_vessel_data", "status": "failed", "error": str(e)}


@celery_app.task(name="ingest_air_quality")
def ingest_air_quality():
    """
    Ingest air quality data from Open-Meteo API.
    Provides real-time and forecast air quality measurements.
    
    Open-Meteo is a free, open-source API with no authentication required.
    Covers PM2.5, PM10, NO2, O3, SO2, CO, and AQI.
    """
    if not settings.enable_real_data_ingestion:
        return {"status": "skipped"}
    
    logger.info("Starting Open-Meteo air quality ingestion...")
    
    try:
        import asyncio
        from backend.connectors.openmeteo_air_quality_connector import (
            OpenMeteoAirQualityConnector,
            GALICIAN_LOCATIONS
        )
        from backend.services.transformers import AirQualityTransformer
        
        connector = OpenMeteoAirQualityConnector(cache_ttl=3600)
        orion = OrionService()
        results = []
        
        # Fetch air quality data for each Galician location
        loop = asyncio.get_event_loop()
        
        for location_name, location_info in GALICIAN_LOCATIONS.items():
            try:
                air_quality_data = loop.run_until_complete(
                    connector.get_air_quality(
                        latitude=location_info["latitude"],
                        longitude=location_info["longitude"],
                        location_name=location_name,
                        forecast_days=5
                    )
                )
                
                if air_quality_data.get("status") == "success":
                    # Normalize the data (synchronously)
                    normalized = loop.run_until_complete(
                        connector.normalize_data(air_quality_data)
                    )
                    
                    # Transform to NGSI-LD AirQualityObserved
                    ngsi_entity = AirQualityTransformer.from_openmeteo(
                        normalized_data=normalized,
                        location_id=location_name,
                        port_code=location_info.get("port", "")
                    )
                    
                    # Publish to Orion
                    if ngsi_entity:
                        response = orion.update_entity(ngsi_entity)
                        results.append({
                            "location": location_name,
                            "status": "published",
                            "aqi": ngsi_entity.get("aqi", {}).get("value")
                        })
                        logger.info(f"Open-Meteo air quality published for {location_name}")
                else:
                    logger.warning(f"Open-Meteo failed for {location_name}: {air_quality_data.get('error')}")
                    results.append({
                        "location": location_name,
                        "status": "failed",
                        "error": air_quality_data.get("error")
                    })
            
            except Exception as e:
                logger.error(f"Error processing Open-Meteo air quality for {location_name}: {str(e)}")
                results.append({
                    "location": location_name,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "task": "ingest_air_quality",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Air quality ingestion failed: {str(e)}")
        return {"task": "ingest_air_quality", "status": "failed", "error": str(e)}


# ============================================================================
# OPEN-METEO MARINE WEATHER INGESTION
# ============================================================================

@celery_app.task(name="ingest_marine_weather_openmeteo")
def ingest_marine_weather_openmeteo():
    """
    Ingest marine weather data from Open-Meteo API.
    Provides wave height, direction, period, and related data.
    
    Open-Meteo is a free, open-source API with no authentication required.
    Perfect complement to official sources for marine data.
    """
    if not settings.enable_real_data_ingestion:
        return {"status": "skipped"}
    
    logger.info("Starting Open-Meteo marine weather ingestion...")
    
    try:
        from backend.connectors.openmeteo_connector import OpenMeteoConnector, GALICIAN_LOCATIONS
        
        connector = OpenMeteoConnector(cache_ttl=3600)
        orion = OrionService()
        results = []
        
        # Fetch marine data for each Galician location
        for location_name, location_info in GALICIAN_LOCATIONS.items():
            try:
                loop = asyncio.get_event_loop()
                marine_data = loop.run_until_complete(
                    connector.get_marine_weather(
                        latitude=location_info["latitude"],
                        longitude=location_info["longitude"],
                        hours=168,
                        past_days=0
                    )
                )
                
                if marine_data.get("status") == "success":
                    # Normalize the data
                    normalized = await connector.normalize_data(marine_data)
                    
                    # Transform to NGSI-LD SeaConditionObserved
                    ngsi_entity = OceanTransformer.from_generic(
                        data=normalized,
                        entity_id=f"urn:ngsi-ld:SeaConditionObserved:openmeteo-{location_name}",
                        source="OpenMeteo",
                        port_code=location_info.get("port", "")
                    )
                    
                    # Publish to Orion
                    if ngsi_entity:
                        response = orion.update_entity(ngsi_entity)
                        results.append({
                            "location": location_name,
                            "status": "published",
                        })
                        logger.info(f"Open-Meteo marine data published for {location_name}")
                else:
                    logger.warning(f"Open-Meteo failed for {location_name}: {marine_data.get('error')}")
                    results.append({
                        "location": location_name,
                        "status": "failed",
                        "error": marine_data.get("error")
                    })
            
            except Exception as e:
                logger.error(f"Error processing Open-Meteo for {location_name}: {str(e)}")
                results.append({
                    "location": location_name,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "task": "ingest_marine_weather_openmeteo",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Open-Meteo marine weather ingestion failed: {str(e)}")
        return {"task": "ingest_marine_weather_openmeteo", "status": "failed", "error": str(e)}
