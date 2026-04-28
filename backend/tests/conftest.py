# Pytest Configuration
# Fixtures and configuration for SmartPort backend tests

import pytest
from pathlib import Path
import sys

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def mock_orion_client():
    """Fixture for mocked Orion-LD client"""
    from unittest.mock import AsyncMock, MagicMock
    
    client = AsyncMock()
    client.query_entities = AsyncMock(return_value=[])
    client.get_entity = AsyncMock(return_value={})
    client.create_entity = AsyncMock(return_value="urn:test:1")
    client.update_entity = AsyncMock(return_value={})
    client.upsert_entity = AsyncMock(return_value={})
    client.delete_entity = AsyncMock(return_value={})
    return client


@pytest.fixture
def sample_port_entity():
    """Fixture for a sample port NGSI-LD entity"""
    return {
        "id": "urn:smartdatamodels:Port:Galicia:CorA",
        "type": "Port",
        "name": {"type": "Property", "value": "Puerto de A Coruña"},
        "country": {"type": "Property", "value": "ES"},
        "imo": {"type": "Property", "value": "ESCOR"},
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [-8.384, 43.371]
            }
        },
    }


@pytest.fixture
def sample_berth_entity():
    """Fixture for a sample berth NGSI-LD entity"""
    return {
        "id": "urn:smartdatamodels:Berth:CorA:berth_A1",
        "type": "Berth",
        "name": {"type": "Property", "value": "A1"},
        "relatedTo": {"type": "Relationship", "object": "urn:smartdatamodels:Port:Galicia:CorA"},
        "status": {"type": "Property", "value": "free"},
        "berthType": {"type": "Property", "value": "general_cargo"},
        "depth": {"type": "Property", "value": 12.5},
        "length": {"type": "Property", "value": 200.0},
        "lastStatusChange": {
            "type": "Property",
            "value": "2026-04-28T10:00:00Z"
        },
    }


@pytest.fixture
def sample_vessel_entity():
    """Fixture for a sample vessel NGSI-LD entity"""
    return {
        "id": "urn:smartdatamodels:Vessel:ImoRegistry:9876543",
        "type": "Vessel",
        "imoNumber": {"type": "Property", "value": "9876543"},
        "name": {"type": "Property", "value": "MSC Example"},
        "vesselType": {"type": "Property", "value": "container_ship"},
        "length": {"type": "Property", "value": 398.0},
        "width": {"type": "Property", "value": 54.0},
        "draft": {"type": "Property", "value": 15.5},
        "grossTonnage": {"type": "Property", "value": 98000},
    }


@pytest.fixture
def sample_authorization_entity():
    """Fixture for a sample authorization NGSI-LD entity"""
    return {
        "id": "urn:smartdatamodels:BoatAuthorized:Galicia:imo9876543",
        "type": "BoatAuthorized",
        "vesselId": {"type": "Relationship", "object": "urn:smartdatamodels:Vessel:ImoRegistry:9876543"},
        "vesselName": {"type": "Property", "value": "MSC Example"},
        "status": {"type": "Property", "value": "authorized"},
        "issuedDate": {"type": "Property", "value": "2025-01-01T00:00:00Z"},
        "expirationDate": {"type": "Property", "value": "2027-12-31T23:59:59Z"},
        "insuranceValid": {"type": "Property", "value": True},
        "insuranceExpiration": {"type": "Property", "value": "2027-06-30T23:59:59Z"},
    }


@pytest.fixture
def sample_portcall_entity():
    """Fixture for a sample PortCall NGSI-LD entity"""
    return {
        "id": "urn:smartdatamodels:PortCall:Galicia:corA_20260430_imo9876543_abc123de",
        "type": "PortCall",
        "vesselId": {"type": "Relationship", "object": "urn:smartdatamodels:Vessel:ImoRegistry:9876543"},
        "portId": {"type": "Relationship", "object": "urn:smartdatamodels:Port:Galicia:CorA"},
        "berthId": {"type": "Relationship", "object": "urn:smartdatamodels:Berth:CorA:berth_A1"},
        "status": {"type": "Property", "value": "scheduled"},
        "estimatedArrival": {"type": "Property", "value": "2026-04-30T08:00:00Z"},
        "estimatedDeparture": {"type": "Property", "value": "2026-05-02T18:00:00Z"},
        "createdAt": {"type": "Property", "value": "2026-04-28T10:00:00Z"},
        "updatedAt": {"type": "Property", "value": "2026-04-28T10:00:00Z"},
    }


@pytest.fixture
def sample_alert_entity():
    """Fixture for a sample alert NGSI-LD entity"""
    return {
        "id": "urn:smartdatamodels:Alert:CorA:alert_001",
        "type": "Alert",
        "portId": {"type": "Relationship", "object": "urn:smartdatamodels:Port:Galicia:CorA"},
        "entityId": {"type": "Property", "value": "urn:smartdatamodels:Vessel:ImoRegistry:9876543"},
        "entityType": {"type": "Property", "value": "Vessel"},
        "alertType": {"type": "Property", "value": "authorization_expired"},
        "severity": {"type": "Property", "value": "critical"},
        "title": {"type": "Property", "value": "Vessel Authorization Expired"},
        "description": {"type": "Property", "value": "Vessel authorization has expired"},
        "isActive": {"type": "Property", "value": True},
        "createdAt": {"type": "Property", "value": "2026-04-28T10:00:00Z"},
    }
