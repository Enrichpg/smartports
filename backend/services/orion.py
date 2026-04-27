# Orion-LD Service Integration
# Handles all communication with FIWARE Orion-LD context broker

from typing import Dict, Any, Optional, List
import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)


class OrionService:
    """Service for interacting with Orion-LD context broker"""

    def __init__(self):
        self.base_url = settings.orion_base_url
        self.headers = {
            "FIWARE-Service": settings.fiware_service,
            "FIWARE-ServicePath": settings.fiware_service_path,
            "Content-Type": "application/ld+json",
        }

    async def get_entities(
        self,
        entity_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get NGSI-LD entities from Orion"""
        try:
            async with httpx.AsyncClient() as client:
                params = {"limit": limit}
                if entity_type:
                    params["type"] = entity_type

                response = await client.get(
                    f"{self.base_url}/ngsi-ld/v1/entities",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching entities from Orion: {e}")
            raise

    async def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """Get a specific NGSI-LD entity"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/ngsi-ld/v1/entities/{entity_id}",
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching entity {entity_id} from Orion: {e}")
            raise

    async def create_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new NGSI-LD entity"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/ngsi-ld/v1/entities",
                    json=entity,
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error creating entity in Orion: {e}")
            raise

    async def update_entity(
        self,
        entity_id: str,
        update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an NGSI-LD entity"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/ngsi-ld/v1/entities/{entity_id}/attrs",
                    json=update,
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error updating entity {entity_id} in Orion: {e}")
            raise


# Singleton instance
orion_service = OrionService()
