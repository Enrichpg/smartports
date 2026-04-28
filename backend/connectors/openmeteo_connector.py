# Open-Meteo Marine Weather Connector
# Free, open-source API for marine weather and wave data

import logging
import pandas as pd
from typing import Any, Dict, Optional
from datetime import datetime
import requests_cache
from retry_requests import retry

logger = logging.getLogger(__name__)


class OpenMeteoConnector:
    """
    Connector for Open-Meteo Marine Weather API.
    
    Open-Meteo provides free marine weather data including:
    - Wave height, direction, period
    - Wind speed and direction
    - Sea surface temperature
    - Currents (where available)
    
    No authentication required. Public API.
    
    Documentation: https://open-meteo.com/en/docs/marine-weather-api
    """
    
    # Marine API endpoint
    MARINE_API_URL = "https://marine-api.open-meteo.com/v1/marine"
    
    # Available variables
    HOURLY_VARIABLES = [
        "wave_height",
        "wave_direction", 
        "wave_period",
        "wind_wave_height",
        "wind_wave_direction",
        "wind_wave_period",
        "swell_wave_height",
        "swell_wave_direction",
        "swell_wave_period",
    ]
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize Open-Meteo connector with caching.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default 1 hour)
        """
        # Setup caching and retry logic
        self.cache_session = requests_cache.CachedSession(
            '.cache/openmeteo',
            expire_after=cache_ttl
        )
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        
        try:
            import openmeteo_requests
            self.client = openmeteo_requests.Client(session=self.retry_session)
        except ImportError:
            logger.warning("openmeteo_requests not installed. Install with: pip install openmeteo-requests")
            self.client = None
    
    async def get_marine_weather(
        self,
        latitude: float,
        longitude: float,
        hours: int = 168,
        past_days: int = 0
    ) -> Dict[str, Any]:
        """
        Get marine weather data for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            hours: Forecast hours (default 168 = 7 days)
            past_days: Historical days to retrieve
            
        Returns:
            Normalized marine weather data
        """
        
        if not self.client:
            return {
                "status": "error",
                "error": "openmeteo_requests library not installed",
                "source": "OpenMeteo"
            }
        
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": ",".join(self.HOURLY_VARIABLES),
                "past_days": past_days,
                "forecast_days": max(1, hours // 24),
                "timezone": "UTC"
            }
            
            logger.info(f"Fetching marine weather for ({latitude}, {longitude})")
            
            responses = self.client.weather_api(self.MARINE_API_URL, params=params)
            response = responses[0]
            
            # Extract hourly data
            hourly = response.Hourly()
            hourly_data = {
                "latitude": response.Latitude(),
                "longitude": response.Longitude(),
                "elevation": response.Elevation(),
                "timezone": response.Timezone(),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "OpenMeteo",
                "status": "success"
            }
            
            # Parse hourly variables into dataframe
            time_index = pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
            
            data_dict = {"time": time_index}
            
            for i, variable_name in enumerate(self.HOURLY_VARIABLES):
                try:
                    values = hourly.Variables(i).ValuesAsNumpy()
                    data_dict[variable_name] = values
                except:
                    pass  # Skip if variable not available
            
            df = pd.DataFrame(data_dict)
            
            # Get latest observation
            latest = df.iloc[-1] if len(df) > 0 else {}
            
            hourly_data["latest"] = {
                "time": latest.get("time", datetime.utcnow()).isoformat() if hasattr(latest.get("time"), "isoformat") else str(latest.get("time")),
                "wave_height": float(latest.get("wave_height", 0)) if latest.get("wave_height") is not None else 0,
                "wave_direction": float(latest.get("wave_direction", 0)) if latest.get("wave_direction") is not None else 0,
                "wave_period": float(latest.get("wave_period", 0)) if latest.get("wave_period") is not None else 0,
                "wind_wave_height": float(latest.get("wind_wave_height", 0)) if latest.get("wind_wave_height") is not None else 0,
                "swell_wave_height": float(latest.get("swell_wave_height", 0)) if latest.get("swell_wave_height") is not None else 0,
            }
            
            # Provide timeseries for 24 hours
            hourly_data["hourly_forecast"] = df.head(24).to_dict("records")
            
            return hourly_data
        
        except Exception as e:
            logger.error(f"Error fetching marine weather from Open-Meteo: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "source": "OpenMeteo"
            }
    
    async def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Open-Meteo response to common format.
        """
        if raw_data.get("status") == "error":
            return raw_data
        
        latest = raw_data.get("latest", {})
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "observed_at": raw_data.get("timestamp"),
            "latitude": raw_data.get("latitude"),
            "longitude": raw_data.get("longitude"),
            
            # Wave data
            "significant_wave_height": latest.get("wave_height"),
            "peak_wave_period": latest.get("wave_period"),
            "mean_wave_direction": latest.get("wave_direction"),
            
            # Wind waves (shorter period)
            "wind_wave_height": latest.get("wind_wave_height"),
            
            # Swell (longer period waves from distant weather systems)
            "swell_wave_height": latest.get("swell_wave_height"),
            
            "source": "OpenMeteo",
            "raw_data": raw_data,
        }


# Galician coastal locations for marine monitoring
GALICIAN_LOCATIONS = {
    "Vigo_Offshore": {
        "latitude": 42.2,
        "longitude": -8.8,
        "port": "80003",
        "description": "Offshore Vigo area (Rias Bajas)"
    },
    "Ferrol_Offshore": {
        "latitude": 43.5,
        "longitude": -8.3,
        "port": "80001",
        "description": "Offshore Ferrol area (Rias Altas)"
    },
    "Corunha_Offshore": {
        "latitude": 43.4,
        "longitude": -8.2,
        "port": "80004",
        "description": "Offshore A Coruña"
    },
    "Atlantic_Reference": {
        "latitude": 42.5,
        "longitude": -9.5,
        "port": None,
        "description": "Atlantic reference point (offshore)"
    },
}
