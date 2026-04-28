# Open-Meteo Air Quality Connector
# Free, open-source API for real-time air quality data

import logging
import pandas as pd
from typing import Any, Dict, Optional
from datetime import datetime
import requests_cache
from retry_requests import retry
import openmeteo_requests

logger = logging.getLogger(__name__)


class OpenMeteoAirQualityConnector:
    """
    Connector for Open-Meteo Air Quality API.
    
    Open-Meteo provides free air quality data including:
    - PM10 (coarse particulate matter)
    - PM2.5 (fine particulate matter)
    - NO2 (nitrogen dioxide)
    - O3 (ozone)
    - SO2 (sulfur dioxide)
    - CO (carbon monoxide)
    - AQI (Air Quality Index)
    
    No authentication required. Public API with 5-day forecasts.
    
    Documentation: https://open-meteo.com/en/docs/air-quality-api
    """
    
    # Air Quality API endpoint
    AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    # Available hourly variables
    HOURLY_VARIABLES = [
        "pm10",
        "pm2_5",
        "nitrogen_dioxide",
        "ozone",
        "sulphur_dioxide",
        "carbon_monoxide",
        "aerosol_optical_depth",
        "dust",
        "uv_index",
        "uv_index_clear_sky",
        "allergen_grass",
        "allergen_ragweed",
        "allergen_birch",
    ]
    
    # Galician monitoring locations (ports + key cities)
    GALICIAN_LOCATIONS = {
        "Vigo": {"latitude": 42.2295, "longitude": -8.7231, "port": "80003"},
        "Ferrol": {"latitude": 43.4734, "longitude": -8.2467, "port": "80001"},
        "Coruña": {"latitude": 43.3734, "longitude": -8.3885, "port": "80004"},
        "Pontevedra": {"latitude": 42.4329, "longitude": -8.6400, "port": "80002"},
        "Lugo": {"latitude": 43.1333, "longitude": -8.5500, "port": "80005"},
    }
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize Open-Meteo Air Quality connector with caching and retry.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default 1 hour)
        """
        # Setup caching and retry logic
        self.cache_session = requests_cache.CachedSession(
            ".cache_air_quality", 
            expire_after=cache_ttl
        )
        self.retry_session = retry(
            self.cache_session,
            retries=5,
            backoff_factor=0.2
        )
        self.client = openmeteo_requests.Client(session=self.retry_session)
        
        logger.info(f"OpenMeteo Air Quality Connector initialized (cache_ttl={cache_ttl}s)")
    
    async def get_air_quality(
        self,
        latitude: float,
        longitude: float,
        location_name: str = "Unknown",
        forecast_days: int = 5,
        past_days: int = 0
    ) -> Dict[str, Any]:
        """
        Fetch air quality data from Open-Meteo API.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            location_name: Human-readable location name
            forecast_days: Number of forecast days (up to 16)
            past_days: Number of past days (up to 92)
        
        Returns:
            Normalized dict with status, source, timestamp, data fields
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": ",".join(self.HOURLY_VARIABLES),
                "forecast_days": forecast_days,
                "past_days": past_days,
                "timezone": "UTC",
            }
            
            logger.info(f"Fetching air quality for {location_name} ({latitude}, {longitude})")
            
            # Make API request
            responses = self.client.weather_api(self.AIR_QUALITY_API_URL, params=params)
            response = responses[0]
            
            # Extract hourly data
            hourly = response.Hourly()
            
            # Parse variables - order matters!
            data_dict = {
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                )
            }
            
            # Map each variable
            for idx, var_name in enumerate(self.HOURLY_VARIABLES):
                try:
                    data_dict[var_name] = hourly.Variables(idx).ValuesAsNumpy()
                except Exception as e:
                    logger.warning(f"Could not extract {var_name}: {str(e)}")
            
            # Create DataFrame
            df = pd.DataFrame(data=data_dict)
            
            # Get latest observation (most recent record)
            latest = df.iloc[-1] if len(df) > 0 else None
            
            if latest is None:
                return {
                    "status": "error",
                    "source": "OpenMeteo",
                    "error": "No data returned from API"
                }
            
            return {
                "status": "success",
                "source": "OpenMeteo",
                "timestamp": datetime.utcnow().isoformat(),
                "location": {
                    "latitude": response.Latitude(),
                    "longitude": response.Longitude(),
                    "name": location_name,
                    "timezone": response.Timezone(),
                },
                "latest": {
                    "pm10": float(latest.get("pm10", 0)) if "pm10" in latest else None,
                    "pm2_5": float(latest.get("pm2_5", 0)) if "pm2_5" in latest else None,
                    "nitrogen_dioxide": float(latest.get("nitrogen_dioxide", 0)) if "nitrogen_dioxide" in latest else None,
                    "ozone": float(latest.get("ozone", 0)) if "ozone" in latest else None,
                    "sulphur_dioxide": float(latest.get("sulphur_dioxide", 0)) if "sulphur_dioxide" in latest else None,
                    "carbon_monoxide": float(latest.get("carbon_monoxide", 0)) if "carbon_monoxide" in latest else None,
                    "uv_index": float(latest.get("uv_index", 0)) if "uv_index" in latest else None,
                },
                "data": df,
                "data_points": len(df)
            }
        
        except Exception as e:
            logger.error(f"Air quality fetch failed for {location_name}: {str(e)}")
            return {
                "status": "error",
                "source": "OpenMeteo",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_all_galician_air_quality(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetch air quality data for all Galician monitoring locations.
        
        Returns:
            Dict mapping location names to their air quality data
        """
        results = {}
        
        for location_name, location_info in self.GALICIAN_LOCATIONS.items():
            try:
                air_quality = await self.get_air_quality(
                    latitude=location_info["latitude"],
                    longitude=location_info["longitude"],
                    location_name=location_name
                )
                results[location_name] = air_quality
            except Exception as e:
                logger.error(f"Failed to fetch air quality for {location_name}: {str(e)}")
                results[location_name] = {
                    "status": "error",
                    "error": str(e),
                    "location": location_name
                }
        
        return results
    
    async def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize air quality data to standard format.
        
        Args:
            raw_data: Raw API response dict
        
        Returns:
            Normalized data dict
        """
        if raw_data.get("status") != "success":
            return {"status": "error", "error": raw_data.get("error")}
        
        latest = raw_data.get("latest", {})
        
        return {
            "status": "success",
            "timestamp": raw_data.get("timestamp"),
            "location": raw_data.get("location"),
            "pm10": latest.get("pm10"),
            "pm2_5": latest.get("pm2_5"),
            "nitrogen_dioxide": latest.get("nitrogen_dioxide"),
            "ozone": latest.get("ozone"),
            "sulphur_dioxide": latest.get("sulphur_dioxide"),
            "carbon_monoxide": latest.get("carbon_monoxide"),
            "uv_index": latest.get("uv_index"),
            "source": "OpenMeteo",
        }
    
    async def calculate_aqi(self, pm2_5: Optional[float], pm10: Optional[float]) -> int:
        """
        Calculate simplified AQI from PM values using EPA formula.
        
        Args:
            pm2_5: PM2.5 concentration in µg/m³
            pm10: PM10 concentration in µg/m³
        
        Returns:
            AQI value (0-500+)
        """
        if pm2_5 is None:
            return 0
        
        # EPA PM2.5 breakpoints (simplified)
        if pm2_5 <= 12:
            aqi = (pm2_5 / 12) * 50
        elif pm2_5 <= 35.4:
            aqi = ((pm2_5 - 12) / (35.4 - 12)) * 50 + 50
        elif pm2_5 <= 55.4:
            aqi = ((pm2_5 - 35.4) / (55.4 - 35.4)) * 50 + 100
        elif pm2_5 <= 150.4:
            aqi = ((pm2_5 - 55.4) / (150.4 - 55.4)) * 50 + 150
        elif pm2_5 <= 250.4:
            aqi = ((pm2_5 - 150.4) / (250.4 - 150.4)) * 50 + 200
        else:
            aqi = ((pm2_5 - 250.4) / 500) * 50 + 250
        
        return int(aqi)
