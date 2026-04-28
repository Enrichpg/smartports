# Vessel Service
# Business logic for vessel queries and management

import logging
from typing import List, Dict, Any
from .orion_ld_client import orion_client
from schemas.vessel import VesselResponse

logger = logging.getLogger(__name__)


class VesselService:
    """Business logic for vessel operations"""

    async def get_all_vessels(
        self, limit: int = 100, offset: int = 0
    ) -> tuple[List[VesselResponse], int]:
        """Get all vessels with pagination"""
        try:
            # Query MasterVessel entities (represent actual vessels)
            entities = await orion_client.query_by_type("Vessel")
            total = len(entities)
            vessels_data = entities[offset : offset + limit]
            vessels = [self._entity_to_vessel_response(v) for v in vessels_data]
            return vessels, total
        except Exception as e:
            logger.error(f"Error fetching vessels: {e}")
            raise

    async def get_vessel_by_id(self, vessel_id: str) -> VesselResponse:
        """Get a specific vessel by ID"""
        try:
            entity = await orion_client.get_entity(vessel_id)
            return self._entity_to_vessel_response(entity)
        except Exception as e:
            logger.error(f"Error fetching vessel {vessel_id}: {e}")
            raise

    async def get_vessel_by_imo(self, imo_number: str) -> VesselResponse:
        """Get vessel by IMO number"""
        try:
            # Query by IMO attribute
            entities = await orion_client.query_entities(
                entity_type="Vessel",
                filters=f"imoNumber=={imo_number}",
                limit=1,
            )
            if not entities:
                raise ValueError(f"Vessel with IMO {imo_number} not found")
            return self._entity_to_vessel_response(entities[0])
        except Exception as e:
            logger.error(f"Error fetching vessel by IMO {imo_number}: {e}")
            raise

    async def get_vessels_by_type(
        self, vessel_type: str, limit: int = 100, offset: int = 0
    ) -> tuple[List[VesselResponse], int]:
        """Get vessels by type"""
        try:
            entities = await orion_client.query_entities(
                entity_type="Vessel", filters=f"vesselType=={vessel_type}", limit=1000
            )
            total = len(entities)
            vessels_data = entities[offset : offset + limit]
            vessels = [self._entity_to_vessel_response(v) for v in vessels_data]
            return vessels, total
        except Exception as e:
            logger.error(f"Error fetching vessels by type {vessel_type}: {e}")
            raise

    def _entity_to_vessel_response(self, entity: Dict[str, Any]) -> VesselResponse:
        """Convert Orion-LD entity to VesselResponse schema"""
        return VesselResponse(
            id=entity.get("id", ""),
            imo_number=entity.get("imoNumber", {}).get("value", ""),
            mmsi=entity.get("mmsi", {}).get("value"),
            name=entity.get("name", {}).get("value", ""),
            vessel_type=entity.get("vesselType", {}).get("value", "unknown"),
            length=entity.get("length", {}).get("value"),
            width=entity.get("width", {}).get("value"),
            draft=entity.get("draft", {}).get("value"),
            gross_tonnage=entity.get("grossTonnage", {}).get("value"),
            deadweight_tonnage=entity.get("deadweightTonnage", {}).get("value"),
            nationality=entity.get("nationality", {}).get("value"),
            operator=entity.get("operator", {}).get("value"),
            status=entity.get("status", {}).get("value"),
        )


# Singleton instance
vessel_service = VesselService()
