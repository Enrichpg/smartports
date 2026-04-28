# Air Quality Data to NGSI-LD Transformer
# Converts Open-Meteo air quality data to NGSI-LD AirQualityObserved

from typing import Any, Dict, Optional
from datetime import datetime


class AirQualityTransformer:
    """
    Transform air quality data from various sources to NGSI-LD AirQualityObserved entity.
    
    NGSI-LD AirQualityObserved schema:
    https://smartdatamodels.org/Environment/AirQualityObserved
    """
    
    # NGSI-LD Context
    CONTEXT = {
        "@context": [
            "https://smartdatamodels.org/context.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]
    }
    
    @staticmethod
    def from_openmeteo(
        normalized_data: Dict[str, Any],
        location_id: str,
        port_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transform Open-Meteo air quality data to NGSI-LD AirQualityObserved.
        
        Args:
            normalized_data: Output from OpenMeteoAirQualityConnector.normalize_data()
            location_id: Location identifier (e.g., "Vigo")
            port_code: Associated port code (optional)
            
        Returns:
            NGSI-LD AirQualityObserved entity
        """
        observed_at = normalized_data.get("timestamp", datetime.utcnow().isoformat())
        location_info = normalized_data.get("location", {})
        
        # Calculate AQI from PM2.5 (simplified EPA formula)
        pm2_5 = normalized_data.get("pm2_5")
        pm10 = normalized_data.get("pm10")
        
        # Calculate AQI
        aqi = AirQualityTransformer._calculate_aqi(pm2_5, pm10)
        
        # Determine AQI level
        aqi_level = AirQualityTransformer._get_aqi_level(aqi)
        
        entity = {
            "@context": AirQualityTransformer.CONTEXT["@context"],
            "id": f"urn:ngsi-ld:AirQualityObserved:openmeteo-{location_id}",
            "type": "AirQualityObserved",
            
            # Location
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [
                        location_info.get("longitude", 0),
                        location_info.get("latitude", 0)
                    ]
                }
            },
            
            # Air Quality Index (overall)
            "aqi": {
                "type": "Property",
                "value": aqi,
                "unitCode": "AQI",
                "observedAt": observed_at
            },
            
            # AQI level (Good, Fair, Moderate, etc.)
            "aqiLevel": {
                "type": "Property",
                "value": aqi_level,
                "observedAt": observed_at
            },
            
            # PM2.5 (fine particulates)
            "pm2_5": {
                "type": "Property",
                "value": pm2_5 if pm2_5 is not None else None,
                "unitCode": "GP",  # microgram per cubic meter
                "observedAt": observed_at
            },
            
            # PM10 (coarse particulates)
            "pm10": {
                "type": "Property",
                "value": pm10 if pm10 is not None else None,
                "unitCode": "GP",
                "observedAt": observed_at
            },
            
            # Nitrogen Dioxide
            "nitrogenDioxide": {
                "type": "Property",
                "value": normalized_data.get("nitrogen_dioxide"),
                "unitCode": "GP",
                "observedAt": observed_at
            },
            
            # Ozone
            "ozone": {
                "type": "Property",
                "value": normalized_data.get("ozone"),
                "unitCode": "GP",
                "observedAt": observed_at
            },
            
            # Sulfur Dioxide
            "sulphurDioxide": {
                "type": "Property",
                "value": normalized_data.get("sulphur_dioxide"),
                "unitCode": "GP",
                "observedAt": observed_at
            },
            
            # Carbon Monoxide
            "carbonMonoxide": {
                "type": "Property",
                "value": normalized_data.get("carbon_monoxide"),
                "unitCode": "GP",
                "observedAt": observed_at
            },
            
            # UV Index
            "uvIndex": {
                "type": "Property",
                "value": normalized_data.get("uv_index"),
                "observedAt": observed_at
            },
            
            # Data source metadata
            "dataProvider": {
                "type": "Property",
                "value": "OpenMeteo"
            },
            
            "sourceConfidence": {
                "type": "Property",
                "value": 0.85  # Open-Meteo is reliable for general air quality
            },
            
            # Location name
            "addressArea": {
                "type": "Property",
                "value": location_info.get("name", location_id)
            },
        }
        
        # Add port relationship if port_code provided
        if port_code:
            entity["relatedPort"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Port:{port_code}"
            }
        
        return entity
    
    @staticmethod
    def _calculate_aqi(pm2_5: Optional[float], pm10: Optional[float]) -> int:
        """
        Calculate AQI from PM values using EPA formula.
        
        Args:
            pm2_5: PM2.5 concentration in µg/m³
            pm10: PM10 concentration in µg/m³
            
        Returns:
            AQI value (0-500+)
        """
        if pm2_5 is None:
            return 0
        
        # EPA PM2.5 breakpoints
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
    
    @staticmethod
    def _get_aqi_level(aqi: int) -> str:
        """
        Get AQI level category from numeric AQI value.
        
        Args:
            aqi: Numeric AQI value
            
        Returns:
            AQI level string (Good, Fair, Moderate, Unhealthy for Sensitive Groups, Unhealthy, Very Unhealthy, Hazardous)
        """
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Fair"
        elif aqi <= 150:
            return "Moderate"
        elif aqi <= 200:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 300:
            return "Unhealthy"
        elif aqi <= 500:
            return "Very Unhealthy"
        else:
            return "Hazardous"
