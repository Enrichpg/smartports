# NGSI-LD Entity Builders
# Construye entidades NGSI-LD válidas según Smart Data Models
# ISO 8601 para timestamps, formato URN consistente, @context incluido

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Global NGSI-LD @context
# Use only the ETSI core context (always cached in Orion-LD) plus an inline
# vocabulary dict. Avoid external URLs that Orion-LD must download at runtime.
NGSI_CONTEXT = [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
    {
        "schema": "https://schema.org/",
        "smartdatamodels": "https://smartdatamodels.org/ontology/",
        "fiware": "https://uri.fiware.org/ns/data-models#",
        "Port": "fiware:Port",
        "Berth": "fiware:Berth",
        "Vessel": "fiware:Vessel",
        "PortCall": "fiware:PortCall",
        "PortAuthority": "fiware:PortAuthority",
        "SeaportFacilities": "fiware:SeaportFacilities",
        "MasterVessel": "fiware:MasterVessel",
        "BoatAuthorized": "fiware:BoatAuthorized",
        "BoatPlacesAvailable": "fiware:BoatPlacesAvailable",
        "BoatPlacesPricing": "fiware:BoatPlacesPricing",
        "Device": "https://uri.fiware.org/ns/data-models#Device",
        "WeatherObserved": "fiware:WeatherObserved",
        "AirQualityObserved": "fiware:AirQualityObserved",
        "Alert": "fiware:Alert",
    }
]


class NGSIBuilder:
    """Base builder for NGSI-LD entities"""
    
    @staticmethod
    def property(value: Any, observed_at: Optional[str] = None) -> Dict[str, Any]:
        """Create NGSI-LD Property"""
        prop = {
            "type": "Property",
            "value": value
        }
        if observed_at:
            prop["observedAt"] = observed_at
        return prop
    
    @staticmethod
    def relationship(object_id: str) -> Dict[str, Any]:
        """Create NGSI-LD Relationship"""
        return {
            "type": "Relationship",
            "object": object_id
        }
    
    @staticmethod
    def geo_property(coordinates: List[float], coord_type: str = "Point") -> Dict[str, Any]:
        """Create NGSI-LD GeoProperty"""
        return {
            "type": "GeoProperty",
            "value": {
                "type": coord_type,
                "coordinates": coordinates
            }
        }


class PortBuilder(NGSIBuilder):
    """Builds Port entities"""
    
    @staticmethod
    def build(
        port_id: str,
        name: str,
        coordinates: List[float],
        description: str = "",
        port_type: str = "SeaPort",
        authority_id: Optional[str] = None,
        facility_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build Port entity"""
        entity = {
            "@context": NGSI_CONTEXT,
            "id": port_id,
            "type": "Port",
            "name": NGSIBuilder.property(name),
            "location": NGSIBuilder.geo_property(coordinates),
            "description": NGSIBuilder.property(description),
            "portType": NGSIBuilder.property(port_type)
        }
        
        if authority_id:
            entity["managedBy"] = NGSIBuilder.relationship(authority_id)
        if facility_id:
            entity["hasFacilities"] = NGSIBuilder.relationship(facility_id)
        
        return entity


class PortAuthorityBuilder(NGSIBuilder):
    """Builds PortAuthority entities"""
    
    @staticmethod
    def build(
        auth_id: str,
        name: str,
        contact_email: str = "",
        contact_phone: str = "",
        website: str = ""
    ) -> Dict[str, Any]:
        """Build PortAuthority entity"""
        return {
            "@context": NGSI_CONTEXT,
            "id": auth_id,
            "type": "PortAuthority",
            "name": NGSIBuilder.property(name),
            "email": NGSIBuilder.property(contact_email),
            "telephone": NGSIBuilder.property(contact_phone),
            "website": NGSIBuilder.property(website)
        }


class SeaportFacilitiesBuilder(NGSIBuilder):
    """Builds SeaportFacilities entities"""
    
    @staticmethod
    def build(
        facility_id: str,
        name: str,
        description: str = "",
        capacity: int = 0,
        port_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build SeaportFacilities entity"""
        entity = {
            "@context": NGSI_CONTEXT,
            "id": facility_id,
            "type": "SeaportFacilities",
            "name": NGSIBuilder.property(name),
            "description": NGSIBuilder.property(description),
            "capacity": NGSIBuilder.property(capacity)
        }
        
        if port_id:
            entity["belongsToPort"] = NGSIBuilder.relationship(port_id)
        
        return entity


class BerthBuilder(NGSIBuilder):
    """Builds Berth entities (dynamic, event-based)"""
    
    @staticmethod
    def build(
        berth_id: str,
        name: str,
        status: str = "free",
        occupied_by: Optional[str] = None,
        facility_id: Optional[str] = None,
        dimensions: Optional[Dict[str, float]] = None,
        updated_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build Berth entity"""
        if updated_at is None:
            updated_at = datetime.utcnow().isoformat() + "Z"
        
        entity = {
            "@context": NGSI_CONTEXT,
            "id": berth_id,
            "type": "Berth",
            "name": NGSIBuilder.property(name),
            "status": NGSIBuilder.property(status, updated_at),
        }
        
        if occupied_by:
            entity["occupiedBy"] = NGSIBuilder.relationship(occupied_by)
        if facility_id:
            entity["belongsTo"] = NGSIBuilder.relationship(facility_id)
        if dimensions:
            entity["dimensions"] = NGSIBuilder.property(dimensions)
        
        return entity


class VesselBuilder(NGSIBuilder):
    """Builds Vessel entities (semi-dynamic)"""
    
    @staticmethod
    def build(
        vessel_id: str,
        name: str,
        mmsi: str,
        imo: str,
        vessel_type: str = "Cargo",
        length: float = 0.0,
        beam: float = 0.0,
        draught: float = 0.0,
        position: Optional[List[float]] = None,
        position_timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build Vessel entity"""
        entity = {
            "@context": NGSI_CONTEXT,
            "id": vessel_id,
            "type": "Vessel",
            "name": NGSIBuilder.property(name),
            "mmsi": NGSIBuilder.property(mmsi),
            "imo": NGSIBuilder.property(imo),
            "vesselType": NGSIBuilder.property(vessel_type),
            "length": NGSIBuilder.property(length),
            "beam": NGSIBuilder.property(beam),
            "draught": NGSIBuilder.property(draught)
        }
        
        if position and position_timestamp:
            entity["location"] = NGSIBuilder.geo_property(position)
            entity["position"] = NGSIBuilder.property(position, position_timestamp)
        
        return entity


class MasterVesselBuilder(NGSIBuilder):
    """Builds MasterVessel entities (static registry)"""
    
    @staticmethod
    def build(
        master_id: str,
        imo: str,
        name: str,
        ship_type: str,
        length: float,
        beam: float,
        depth: float,
        gross_tonnage: int = 0,
        net_tonnage: int = 0,
        year_built: int = 0,
        flag_state: str = "ES"
    ) -> Dict[str, Any]:
        """Build MasterVessel entity (static registry)"""
        return {
            "@context": NGSI_CONTEXT,
            "id": master_id,
            "type": "MasterVessel",
            "imo": NGSIBuilder.property(imo),
            "name": NGSIBuilder.property(name),
            "shipType": NGSIBuilder.property(ship_type),
            "length": NGSIBuilder.property(length),
            "beam": NGSIBuilder.property(beam),
            "depth": NGSIBuilder.property(depth),
            "grossTonnage": NGSIBuilder.property(gross_tonnage),
            "netTonnage": NGSIBuilder.property(net_tonnage),
            "yearBuilt": NGSIBuilder.property(year_built),
            "flagState": NGSIBuilder.property(flag_state)
        }


class BoatAuthorizedBuilder(NGSIBuilder):
    """Builds BoatAuthorized entities"""
    
    @staticmethod
    def build(
        auth_id: str,
        vessel_id: str,
        authorized_port: str,
        valid_from: str,
        valid_until: str,
        authorization_type: str = "recreational"
    ) -> Dict[str, Any]:
        """Build BoatAuthorized entity"""
        return {
            "@context": NGSI_CONTEXT,
            "id": auth_id,
            "type": "BoatAuthorized",
            "refVessel": NGSIBuilder.relationship(vessel_id),
            "authorizedPort": NGSIBuilder.property(authorized_port),
            "validFrom": NGSIBuilder.property(valid_from),
            "validUntil": NGSIBuilder.property(valid_until),
            "authorizationType": NGSIBuilder.property(authorization_type)
        }


class BoatPlacesAvailableBuilder(NGSIBuilder):
    """Builds BoatPlacesAvailable entities"""
    
    @staticmethod
    def build(
        availability_id: str,
        facility_id: str,
        category: str,
        total_places: int,
        available_places: int,
        updated_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build BoatPlacesAvailable entity"""
        if updated_at is None:
            updated_at = datetime.utcnow().isoformat() + "Z"
        
        return {
            "@context": NGSI_CONTEXT,
            "id": availability_id,
            "type": "BoatPlacesAvailable",
            "refSeaportFacility": NGSIBuilder.relationship(facility_id),
            "category": NGSIBuilder.property(category),
            "totalPlaces": NGSIBuilder.property(total_places),
            "availablePlaces": NGSIBuilder.property(available_places, updated_at)
        }


class BoatPlacesPricingBuilder(NGSIBuilder):
    """Builds BoatPlacesPricing entities"""
    
    @staticmethod
    def build(
        pricing_id: str,
        facility_id: str,
        category: str,
        price_per_day: float,
        currency: str = "EUR",
        iso8266_length_min: Optional[float] = None,
        iso8266_length_max: Optional[float] = None
    ) -> Dict[str, Any]:
        """Build BoatPlacesPricing entity"""
        entity = {
            "@context": NGSI_CONTEXT,
            "id": pricing_id,
            "type": "BoatPlacesPricing",
            "refSeaportFacility": NGSIBuilder.relationship(facility_id),
            "category": NGSIBuilder.property(category),
            "pricePerDay": NGSIBuilder.property(price_per_day),
            "currency": NGSIBuilder.property(currency)
        }
        
        if iso8266_length_min:
            entity["iso8266LengthMin"] = NGSIBuilder.property(iso8266_length_min)
        if iso8266_length_max:
            entity["iso8266LengthMax"] = NGSIBuilder.property(iso8266_length_max)
        
        return entity


class DeviceBuilder(NGSIBuilder):
    """Builds Device entities (sensors)"""
    
    @staticmethod
    def build(
        device_id: str,
        name: str,
        device_type: str,
        location: List[float],
        controlled_asset: Optional[str] = None,
        port_ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build Device entity"""
        entity = {
            "@context": NGSI_CONTEXT,
            "id": device_id,
            "type": "Device",
            "name": NGSIBuilder.property(name),
            "deviceType": NGSIBuilder.property(device_type),
            "location": NGSIBuilder.geo_property(location)
        }
        
        if controlled_asset:
            entity["controlledAsset"] = NGSIBuilder.relationship(controlled_asset)
        if port_ref:
            entity["refPort"] = NGSIBuilder.relationship(port_ref)
        
        return entity


class AirQualityObservedBuilder(NGSIBuilder):
    """Builds AirQualityObserved entities"""
    
    @staticmethod
    def build(
        obs_id: str,
        device_id: str,
        location: List[float],
        observed_at: str,
        pm25: float,
        pm10: float,
        no2: Optional[float] = None,
        co: Optional[float] = None,
        so2: Optional[float] = None
    ) -> Dict[str, Any]:
        """Build AirQualityObserved entity"""
        entity = {
            "@context": NGSI_CONTEXT,
            "id": obs_id,
            "type": "AirQualityObserved",
            "refDevice": NGSIBuilder.relationship(device_id),
            "location": NGSIBuilder.geo_property(location),
            "observedAt": observed_at,
            "pm25": NGSIBuilder.property(pm25, observed_at),
            "pm10": NGSIBuilder.property(pm10, observed_at)
        }
        
        if no2 is not None:
            entity["no2"] = NGSIBuilder.property(no2, observed_at)
        if co is not None:
            entity["co"] = NGSIBuilder.property(co, observed_at)
        if so2 is not None:
            entity["so2"] = NGSIBuilder.property(so2, observed_at)
        
        return entity


class WeatherObservedBuilder(NGSIBuilder):
    """Builds WeatherObserved entities"""
    
    @staticmethod
    def build(
        obs_id: str,
        device_id: str,
        location: List[float],
        observed_at: str,
        temperature: float,
        relative_humidity: float,
        wind_speed: float,
        wind_direction: Optional[float] = None,
        atmospheric_pressure: Optional[float] = None
    ) -> Dict[str, Any]:
        """Build WeatherObserved entity"""
        entity = {
            "@context": NGSI_CONTEXT,
            "id": obs_id,
            "type": "WeatherObserved",
            "refDevice": NGSIBuilder.relationship(device_id),
            "location": NGSIBuilder.geo_property(location),
            "observedAt": observed_at,
            "temperature": NGSIBuilder.property(temperature, observed_at),
            "relativeHumidity": NGSIBuilder.property(relative_humidity, observed_at),
            "windSpeed": NGSIBuilder.property(wind_speed, observed_at)
        }
        
        if wind_direction is not None:
            entity["windDirection"] = NGSIBuilder.property(wind_direction, observed_at)
        if atmospheric_pressure is not None:
            entity["atmosphericPressure"] = NGSIBuilder.property(atmospheric_pressure, observed_at)
        
        return entity


class AlertBuilder(NGSIBuilder):
    """Builds Alert entities"""
    
    @staticmethod
    def build(
        alert_id: str,
        alert_type: str,
        severity: str,
        description: str,
        affected_entity: str,
        created_at: str,
        status: str = "active"
    ) -> Dict[str, Any]:
        """Build Alert entity"""
        return {
            "@context": NGSI_CONTEXT,
            "id": alert_id,
            "type": "Alert",
            "alertType": NGSIBuilder.property(alert_type),
            "severity": NGSIBuilder.property(severity),
            "description": NGSIBuilder.property(description),
            "affectedEntity": NGSIBuilder.relationship(affected_entity),
            "createdAt": NGSIBuilder.property(created_at),
            "status": NGSIBuilder.property(status)
        }
