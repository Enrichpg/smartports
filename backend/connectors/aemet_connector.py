# AEMET OpenData Connector
# Spanish Weather Service official API for meteorological data

import logging
from typing import Any, Dict, Optional
from datetime import datetime
from .base_connector import BaseConnector

logger = logging.getLogger(__name__)


class AEMETConnector(BaseConnector):
    """
    Connector for AEMET OpenData API.
    
    AEMET OpenData is Spain's official meteorological service API.
    Provides weather observations, forecasts, and alerts.
    
    API: https://opendata.aemet.es/opendata
    """
    
    def __init__(self, api_key: str, base_url: str = "https://opendata.aemet.es/opendata"):
        super().__init__(api_key=api_key, base_url=base_url)
    
    async def get_weather_data(self, location_code: str) -> Dict[str, Any]:
        """
        Get weather observation for a specific AEMET station.
        
        Args:
            location_code: AEMET station code (e.g., '35012', '36037')
            
        Returns:
            Normalized weather data with source metadata
        """
        endpoint = f"/api/observacion/convencional/datos/{location_code}"
        params = {"api_key": self.api_key}
        
        result = await self.fetch(endpoint, params=params)
        
        if result["status"] == "success":
            try:
                normalized = await self.normalize_data(result["data"])
                return {**normalized, "source": "AEMET"}
            except Exception as e:
                logger.error(f"AEMET normalization error: {str(e)}")
                return {"status": "error", "error": str(e), "source": "AEMET"}
        
        return result
    
    async def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize AEMET API response to common weather format.
        
        AEMET returns nested structure with observation data.
        Extract key meteorological variables.
        """
        try:
            if isinstance(raw_data, dict) and "datos" in raw_data:
                obs = raw_data["datos"]
            else:
                obs = raw_data
            
            if not obs:
                return {"status": "error", "error": "No observation data"}
            
            # Get latest observation (usually first element)
            latest = obs[0] if isinstance(obs, list) else obs
            
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "observed_at": latest.get("fecobs", datetime.utcnow().isoformat()),
                "temperature": float(latest.get("ta", 0)),  # Air temperature
                "humidity": float(latest.get("hr", 0)),  # Relative humidity
                "pressure": float(latest.get("pres", 0)),  # Pressure
                "wind_speed": float(latest.get("vv", 0)),  # Wind speed
                "wind_direction": float(latest.get("dv", 0)),  # Wind direction
                "precipitation": float(latest.get("prec", 0)),  # Precipitation
                "raw_data": latest,
            }
        except Exception as e:
            logger.error(f"AEMET normalization failed: {str(e)}")
            raise
    
    async def get_forecast(self, location_code: str) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            location_code: AEMET location code
            
        Returns:
            Forecast data
        """
        endpoint = f"/api/prediccion/especifica/municipios/{location_code}"
        params = {"api_key": self.api_key}
        
        return await self.fetch(endpoint, params=params)
    
    async def get_alerts(self) -> Dict[str, Any]:
        """Get active weather alerts for Galicia"""
        endpoint = "/api/avisos/avisosAct"
        params = {"api_key": self.api_key}
        
        return await self.fetch(endpoint, params=params)


# Galician stations mapping (AEMET codes)
GALICIAN_STATIONS = {
    "Vigo": "35012",
    "Pontevedra": "36037",
    "Ourense": "32022",
    "Lugo": "27039",
    "Coruna": "15001",
    "Ferrol": "15023",
}
