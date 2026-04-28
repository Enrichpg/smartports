# Availability and Operational Data to NGSI-LD Transformer
# Converts berth availability, boat places, and operational status

from typing import Any, Dict
from datetime import datetime


class AvailabilityTransformer:
    """
    Transform availability data (berth status, boat places, etc.) to NGSI-LD entities.
    
    Handles both real-derived data and simulated fallback data.
    """
    
    CONTEXT = {
        "@context": [
            "https://smartdatamodels.org/context.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]
    }
    
    @staticmethod
    def berth_status(
        berth_id: str,
        port_code: str,
        status: str,
        occupied: bool,
        occupant_vessel_id: str = None,
        data_source: str = "simulator",
        confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Create NGSI-LD Berth entity with status.
        
        Args:
            berth_id: Berth identifier
            port_code: Associated port
            status: "free", "occupied", "maintenance", "blocked"
            occupied: Whether berth is occupied
            occupant_vessel_id: ID of occupant vessel (if occupied)
            data_source: "real", "derived", or "simulator"
            confidence: Data confidence (0-1)
            
        Returns:
            NGSI-LD Berth entity
        """
        
        entity = {
            "@context": AvailabilityTransformer.CONTEXT["@context"],
            "id": f"urn:ngsi-ld:Berth:{berth_id}",
            "type": "Berth",
            
            "port": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Port:{port_code}"
            },
            
            "status": {
                "type": "Property",
                "value": status,
                "observedAt": datetime.utcnow().isoformat()
            },
            
            "occupied": {
                "type": "Property",
                "value": occupied,
                "observedAt": datetime.utcnow().isoformat()
            },
            
            "dataSource": {
                "type": "Property",
                "value": data_source
            },
            
            "sourceConfidence": {
                "type": "Property",
                "value": confidence
            }
        }
        
        # Add occupant if present
        if occupant_vessel_id and occupied:
            entity["occupiedBy"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Vessel:{occupant_vessel_id}"
            }
        
        return entity
    
    @staticmethod
    def boat_places_available(
        port_code: str,
        port_type: str,
        available_places: int,
        total_places: int,
        data_source: str = "simulator"
    ) -> Dict[str, Any]:
        """
        Create NGSI-LD BoatPlacesAvailable entity.
        
        Args:
            port_code: Port identifier
            port_type: "mooring", "berth", "anchorage"
            available_places: Number of available places
            total_places: Total places of this type
            data_source: Origin of data ("real", "derived", "simulator")
            
        Returns:
            NGSI-LD BoatPlacesAvailable entity
        """
        
        occupancy_rate = 1 - (available_places / total_places) if total_places > 0 else 0
        
        entity = {
            "@context": AvailabilityTransformer.CONTEXT["@context"],
            "id": f"urn:ngsi-ld:BoatPlacesAvailable:{port_code}-{port_type}",
            "type": "BoatPlacesAvailable",
            
            "refPort": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Port:{port_code}"
            },
            
            "placeType": {
                "type": "Property",
                "value": port_type
            },
            
            "availablePlaces": {
                "type": "Property",
                "value": available_places,
                "observedAt": datetime.utcnow().isoformat()
            },
            
            "totalPlaces": {
                "type": "Property",
                "value": total_places
            },
            
            "occupancyRate": {
                "type": "Property",
                "value": occupancy_rate,
                "observedAt": datetime.utcnow().isoformat()
            },
            
            "dataSource": {
                "type": "Property",
                "value": data_source
            },
            
            "dateObserved": {
                "type": "Property",
                "value": datetime.utcnow().isoformat()
            }
        }
        
        return entity
    
    @staticmethod
    def vessel_status(
        vessel_id: str,
        mmsi: int,
        port_code: str,
        status: str,
        current_berth: str = None,
        data_source: str = "real"
    ) -> Dict[str, Any]:
        """
        Create NGSI-LD Vessel entity with status.
        
        Args:
            vessel_id: Vessel identifier
            mmsi: Maritime Mobile Service Identity
            port_code: Port where vessel is/will be
            status: "moored", "underway", "at_anchor", "transiting"
            current_berth: Berth ID if moored
            data_source: Data origin
            
        Returns:
            NGSI-LD Vessel entity
        """
        
        entity = {
            "@context": AvailabilityTransformer.CONTEXT["@context"],
            "id": f"urn:ngsi-ld:Vessel:{vessel_id}",
            "type": "Vessel",
            
            "mmsi": {
                "type": "Property",
                "value": mmsi
            },
            
            "status": {
                "type": "Property",
                "value": status,
                "observedAt": datetime.utcnow().isoformat()
            },
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [0, 0]
                },
                "observedAt": datetime.utcnow().isoformat()
            },
            
            "atPort": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Port:{port_code}"
            },
            
            "dataSource": {
                "type": "Property",
                "value": data_source
            }
        }
        
        if current_berth:
            entity["moored At"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Berth:{current_berth}"
            }
        
        return entity
