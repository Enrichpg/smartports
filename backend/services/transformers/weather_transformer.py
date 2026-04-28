# Weather Data to NGSI-LD Transformer
# Converts AEMET, MeteoGalicia, and other weather sources to NGSI-LD WeatherObserved

from typing import Any, Dict
from datetime import datetime


class WeatherTransformer:
    """
    Transform weather data from various sources to NGSI-LD WeatherObserved entity.
    
    NGSI-LD WeatherObserved schema: https://smartdatamodels.org/Weather/WeatherObserved
    """
    
    # NGSI-LD Context
    CONTEXT = {
        "@context": [
            "https://smartdatamodels.org/context.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]
    }
    
    @staticmethod
    def from_aemet(
        normalized_data: Dict[str, Any],
        location_id: str,
        port_code: str
    ) -> Dict[str, Any]:
        """
        Transform AEMET normalized data to NGSI-LD WeatherObserved.
        
        Args:
            normalized_data: Output from AEMETConnector.normalize_data()
            location_id: AEMET station ID
            port_code: Associated port code
            
        Returns:
            NGSI-LD WeatherObserved entity
        """
        observed_at = normalized_data.get("observed_at", datetime.utcnow().isoformat())
        
        entity = {
            "@context": WeatherTransformer.CONTEXT["@context"],
            "id": f"urn:ngsi-ld:WeatherObserved:aemet-{location_id}",
            "type": "WeatherObserved",
            
            # Core properties
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [0, 0]  # Will be filled with actual coordinates
                }
            },
            
            # Temperature
            "temperature": {
                "type": "Property",
                "value": normalized_data.get("temperature", 0),
                "unitCode": "CEL",
                "observedAt": observed_at
            },
            
            # Humidity
            "relativeHumidity": {
                "type": "Property",
                "value": normalized_data.get("humidity", 0) / 100,  # Convert to 0-1 range
                "observedAt": observed_at
            },
            
            # Pressure
            "atmosphericPressure": {
                "type": "Property",
                "value": normalized_data.get("pressure", 0),
                "unitCode": "PA",
                "observedAt": observed_at
            },
            
            # Wind
            "windSpeed": {
                "type": "Property",
                "value": normalized_data.get("wind_speed", 0),
                "unitCode": "MTS",
                "observedAt": observed_at
            },
            
            "windDirection": {
                "type": "Property",
                "value": normalized_data.get("wind_direction", 0),
                "unitCode": "DD",
                "observedAt": observed_at
            },
            
            # Precipitation
            "precipitation": {
                "type": "Property",
                "value": normalized_data.get("precipitation", 0),
                "unitCode": "MMT",
                "observedAt": observed_at
            },
            
            # Data provenance
            "dataProvider": {
                "type": "Property",
                "value": "AEMET"
            },
            
            "source": {
                "type": "Property",
                "value": "AEMET OpenData"
            },
            
            # Relationships
            "refPort": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Port:{port_code}"
            },
            
            # Metadata
            "dateObserved": {
                "type": "Property",
                "value": observed_at
            }
        }
        
        return entity
    
    @staticmethod
    def from_meteogalicia(
        normalized_data: Dict[str, Any],
        location_id: str,
        port_code: str
    ) -> Dict[str, Any]:
        """Transform MeteoGalicia data to NGSI-LD WeatherObserved"""
        
        entity = {
            "@context": WeatherTransformer.CONTEXT["@context"],
            "id": f"urn:ngsi-ld:WeatherObserved:meteogalicia-{location_id}",
            "type": "WeatherObserved",
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [0, 0]
                }
            },
            
            "dataProvider": {
                "type": "Property",
                "value": "MeteoGalicia"
            },
            
            "source": {
                "type": "Property",
                "value": "MeteoGalicia WMS/WCS Services"
            },
            
            "refPort": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Port:{port_code}"
            },
            
            "dateObserved": {
                "type": "Property",
                "value": datetime.utcnow().isoformat()
            }
        }
        
        return entity
    
    @staticmethod
    def from_generic(
        data: Dict[str, Any],
        entity_id: str,
        source: str,
        port_code: str
    ) -> Dict[str, Any]:
        """
        Generic transformer for any weather source.
        Fills only the fields that are available in the input data.
        """
        
        entity = {
            "@context": WeatherTransformer.CONTEXT["@context"],
            "id": entity_id,
            "type": "WeatherObserved",
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": data.get("coordinates", [0, 0])
                }
            },
            
            "dataProvider": {
                "type": "Property",
                "value": source
            },
            
            "refPort": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Port:{port_code}"
            },
            
            "dateObserved": {
                "type": "Property",
                "value": data.get("observed_at", datetime.utcnow().isoformat())
            }
        }
        
        # Add optional fields if present
        if "temperature" in data:
            entity["temperature"] = {
                "type": "Property",
                "value": data["temperature"],
                "unitCode": "CEL",
                "observedAt": data.get("observed_at", datetime.utcnow().isoformat())
            }
        
        if "humidity" in data:
            entity["relativeHumidity"] = {
                "type": "Property",
                "value": data["humidity"],
                "observedAt": data.get("observed_at", datetime.utcnow().isoformat())
            }
        
        if "wind_speed" in data:
            entity["windSpeed"] = {
                "type": "Property",
                "value": data["wind_speed"],
                "unitCode": "MTS",
                "observedAt": data.get("observed_at", datetime.utcnow().isoformat())
            }
        
        return entity
