# Ocean Data to NGSI-LD Transformer
# Converts Puertos del Estado and other oceanographic sources to NGSI-LD entities

from typing import Any, Dict
from datetime import datetime


class OceanTransformer:
    """
    Transform oceanographic data to NGSI-LD SeaConditionObserved entity.
    
    NGSI-LD reference: https://smartdatamodels.org/SeaCondition/
    """
    
    CONTEXT = {
        "@context": [
            "https://smartdatamodels.org/context.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]
    }
    
    @staticmethod
    def from_puertos_estado(
        normalized_data: Dict[str, Any],
        station_id: str,
        port_code: str
    ) -> Dict[str, Any]:
        """
        Transform Puertos del Estado data to NGSI-LD SeaConditionObserved.
        
        Args:
            normalized_data: Normalized oceanographic data
            station_id: Station/buoy identifier
            port_code: Associated port code
            
        Returns:
            NGSI-LD SeaConditionObserved entity
        """
        sea_state = normalized_data.get("sea_state", {})
        observed_at = normalized_data.get("timestamp", datetime.utcnow().isoformat())
        
        entity = {
            "@context": OceanTransformer.CONTEXT["@context"],
            "id": f"urn:ngsi-ld:SeaConditionObserved:puertosdelestado-{station_id}",
            "type": "SeaConditionObserved",
            
            # Location
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": normalized_data.get("coordinates", [0, 0])
                }
            },
            
            # Significant wave height (m)
            "significantWaveHeight": {
                "type": "Property",
                "value": sea_state.get("significant_wave_height"),
                "unitCode": "MTR",
                "observedAt": observed_at
            },
            
            # Wave peak period (s)
            "wavePeakPeriod": {
                "type": "Property",
                "value": sea_state.get("peak_period"),
                "unitCode": "SEC",
                "observedAt": observed_at
            },
            
            # Wave mean direction (degrees)
            "waveMeanDirection": {
                "type": "Property",
                "value": sea_state.get("mean_direction"),
                "unitCode": "DD",
                "observedAt": observed_at
            },
            
            # Wind
            "windSpeed": {
                "type": "Property",
                "value": sea_state.get("wind_speed"),
                "unitCode": "MTS",
                "observedAt": observed_at
            },
            
            "windDirection": {
                "type": "Property",
                "value": sea_state.get("wind_direction"),
                "unitCode": "DD",
                "observedAt": observed_at
            },
            
            # Water properties
            "waterTemperature": {
                "type": "Property",
                "value": sea_state.get("water_temperature"),
                "unitCode": "CEL",
                "observedAt": observed_at
            },
            
            # Tide
            "tideLevel": {
                "type": "Property",
                "value": sea_state.get("tide_level"),
                "unitCode": "MTR",
                "observedAt": observed_at
            },
            
            # Currents
            "currentSpeed": {
                "type": "Property",
                "value": sea_state.get("current_speed"),
                "unitCode": "MTS",
                "observedAt": observed_at
            },
            
            # Data provenance
            "dataProvider": {
                "type": "Property",
                "value": "Puertos_del_Estado"
            },
            
            "source": {
                "type": "Property",
                "value": "Puertos del Estado Measurement Networks"
            },
            
            # Relationships
            "refPort": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Port:{port_code}"
            },
            
            "dateObserved": {
                "type": "Property",
                "value": observed_at
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
        Generic oceanographic transformer.
        Fills available fields from input data.
        """
        
        entity = {
            "@context": OceanTransformer.CONTEXT["@context"],
            "id": entity_id,
            "type": "SeaConditionObserved",
            
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
        
        # Add optional fields
        optional_fields = {
            "significantWaveHeight": ("significant_wave_height", "MTR"),
            "waterTemperature": ("water_temperature", "CEL"),
            "tideLevel": ("tide_level", "MTR"),
            "windSpeed": ("wind_speed", "MTS"),
        }
        
        for ngsi_field, (data_key, unit_code) in optional_fields.items():
            if data_key in data and data[data_key] is not None:
                entity[ngsi_field] = {
                    "type": "Property",
                    "value": data[data_key],
                    "unitCode": unit_code,
                    "observedAt": data.get("observed_at", datetime.utcnow().isoformat())
                }
        
        return entity
