"""
NGSI-LD Payload Validator
Validates generated payloads for NGSI-LD compliance before loading to Orion-LD

Usage:
    python validate_payloads.py
"""

import json
import sys
from typing import Dict, Any, List

sys.path.insert(0, '/home/enrique/XDEI/SmartPorts')

from backend.services.ngsi_builders import (
    PortBuilder, PortAuthorityBuilder, SeaportFacilitiesBuilder,
    BerthBuilder, VesselBuilder, MasterVesselBuilder, BoatAuthorizedBuilder,
    BoatPlacesAvailableBuilder, BoatPlacesPricingBuilder, DeviceBuilder,
    AirQualityObservedBuilder, WeatherObservedBuilder, AlertBuilder
)
from data.catalogs.galicia_ports import GALICIAN_PORTS


class NGSIValidator:
    """Validates NGSI-LD payloads"""
    
    @staticmethod
    def validate_payload(entity: Dict[str, Any]) -> List[str]:
        """Validate a single entity payload"""
        errors = []
        
        # Check required fields
        if "@context" not in entity:
            errors.append("Missing @context")
        
        if "id" not in entity:
            errors.append("Missing id")
        elif not entity["id"].startswith("urn:ngsi-ld:"):
            errors.append(f"Invalid URN format: {entity['id']}")
        
        if "type" not in entity:
            errors.append("Missing type")
        
        # Check that all non-metadata fields are Property, Relationship, or GeoProperty
        valid_ngsi_types = {"Property", "Relationship", "GeoProperty"}
        
        for key, value in entity.items():
            if key in ["@context", "id", "type"]:
                continue
            
            if isinstance(value, dict):
                if "type" in value:
                    if value["type"] not in valid_ngsi_types:
                        errors.append(f"Field '{key}' has invalid type: {value['type']}")
                else:
                    errors.append(f"Field '{key}' missing 'type' field")
        
        return errors
    
    @staticmethod
    def validate_all_entities() -> Dict[str, Any]:
        """Generate and validate all entities"""
        results = {
            "total_errors": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "entities": []
        }
        
        # Generate sample entities
        test_entities = []
        
        # Port
        port_id = "urn:ngsi-ld:Port:galicia-test"
        authority_id = "urn:ngsi-ld:PortAuthority:autoridad-test"
        facility_id = "urn:ngsi-ld:SeaportFacilities:galicia-test-main"
        
        test_entities.append(PortBuilder.build(
            port_id=port_id,
            name="Test Port",
            coordinates=[-8.5, 43.0],
            authority_id=authority_id,
            facility_id=facility_id
        ))
        
        # PortAuthority
        test_entities.append(PortAuthorityBuilder.build(
            auth_id=authority_id,
            name="Test Authority",
            contact_email="test@port.es"
        ))
        
        # SeaportFacilities
        test_entities.append(SeaportFacilitiesBuilder.build(
            facility_id=facility_id,
            name="Test Facility",
            capacity=250,
            port_id=port_id
        ))
        
        # Berth
        test_entities.append(BerthBuilder.build(
            berth_id="urn:ngsi-ld:Berth:galicia-test-001",
            name="Test Berth",
            status="free",
            facility_id=facility_id
        ))
        
        # MasterVessel
        test_entities.append(MasterVesselBuilder.build(
            master_id="urn:ngsi-ld:MasterVessel:imo-9999999",
            imo="9999999",
            name="Test Vessel",
            ship_type="General Cargo",
            length=120.0,
            beam=18.0,
            depth=10.0
        ))
        
        # Vessel
        test_entities.append(VesselBuilder.build(
            vessel_id="urn:ngsi-ld:Vessel:mmsi-999999999",
            name="Test Vessel Instance",
            mmsi="999999999",
            imo="9999999",
            vessel_type="General Cargo",
            length=120.0,
            beam=18.0,
            draught=10.0,
            position=[-8.5, 43.0],
            position_timestamp="2026-04-27T12:00:00Z"
        ))
        
        # BoatAuthorized
        test_entities.append(BoatAuthorizedBuilder.build(
            auth_id="urn:ngsi-ld:BoatAuthorized:es-999999999",
            vessel_id="urn:ngsi-ld:Vessel:mmsi-999999999",
            authorized_port="test",
            valid_from="2026-04-27T00:00:00Z",
            valid_until="2027-04-27T00:00:00Z"
        ))
        
        # BoatPlacesAvailable
        test_entities.append(BoatPlacesAvailableBuilder.build(
            availability_id="urn:ngsi-ld:BoatPlacesAvailable:galicia-test-A",
            facility_id=facility_id,
            category="A",
            total_places=50,
            available_places=35
        ))
        
        # BoatPlacesPricing
        test_entities.append(BoatPlacesPricingBuilder.build(
            pricing_id="urn:ngsi-ld:BoatPlacesPricing:galicia-test-cat-A",
            facility_id=facility_id,
            category="A",
            price_per_day=45.0,
            iso8266_length_min=0,
            iso8266_length_max=7
        ))
        
        # Device
        test_entities.append(DeviceBuilder.build(
            device_id="urn:ngsi-ld:Device:galicia-test-air-01",
            name="Test Air Quality Sensor",
            device_type="AirQualityMeter",
            location=[-8.5, 43.0],
            port_ref=port_id
        ))
        
        # AirQualityObserved
        test_entities.append(AirQualityObservedBuilder.build(
            obs_id="urn:ngsi-ld:AirQualityObserved:galicia-test-air-01",
            device_id="urn:ngsi-ld:Device:galicia-test-air-01",
            location=[-8.5, 43.0],
            observed_at="2026-04-27T12:00:00Z",
            pm25=15.5,
            pm10=25.0
        ))
        
        # WeatherObserved
        test_entities.append(WeatherObservedBuilder.build(
            obs_id="urn:ngsi-ld:WeatherObserved:galicia-test-weather-01",
            device_id="urn:ngsi-ld:Device:galicia-test-air-01",
            location=[-8.5, 43.0],
            observed_at="2026-04-27T12:00:00Z",
            temperature=18.5,
            relative_humidity=65.0,
            wind_speed=12.0
        ))
        
        # Validate all
        for entity in test_entities:
            errors = NGSIValidator.validate_payload(entity)
            
            entity_result = {
                "id": entity.get("id"),
                "type": entity.get("type"),
                "valid": len(errors) == 0,
                "errors": errors
            }
            
            results["entities"].append(entity_result)
            results["total_errors"] += len(errors)
            
            if len(errors) == 0:
                results["valid_count"] += 1
            else:
                results["invalid_count"] += 1
        
        return results


def print_results(results: Dict[str, Any]):
    """Pretty print validation results"""
    print("\n" + "="*80)
    print("NGSI-LD PAYLOAD VALIDATION REPORT")
    print("="*80)
    
    print(f"\nTotal Entities Tested: {len(results['entities'])}")
    print(f"Valid:   {results['valid_count']}")
    print(f"Invalid: {results['invalid_count']}")
    print(f"Total Errors: {results['total_errors']}")
    
    print("\n" + "-"*80)
    print("ENTITY DETAILS")
    print("-"*80)
    
    for entity in results["entities"]:
        status = "✓ VALID" if entity["valid"] else "✗ INVALID"
        print(f"\n{status} - {entity['type']} ({entity['id']})")
        
        if entity["errors"]:
            for error in entity["errors"]:
                print(f"  ERROR: {error}")
    
    print("\n" + "="*80)
    
    if results["invalid_count"] == 0:
        print("✓ ALL PAYLOADS VALID - Ready for Orion-LD")
    else:
        print(f"✗ {results['invalid_count']} PAYLOADS INVALID - Fix errors before loading")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    print("Validating NGSI-LD Payloads...")
    results = NGSIValidator.validate_all_entities()
    print_results(results)
    
    sys.exit(0 if results["invalid_count"] == 0 else 1)
