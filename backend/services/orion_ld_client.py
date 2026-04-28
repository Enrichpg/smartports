# Orion-LD Client Service
# Low-level HTTP client for NGSI-LD context broker interactions

import httpx
import json
import logging
from typing import Optional, Dict, List, Any
from config import settings

logger = logging.getLogger(__name__)


class OrionLDClient:
    """
    HTTP client for Orion-LD context broker.
    Handles NGSI-LD queries, entity creation/update, and subscriptions.
    """

    def __init__(self):
        self.base_url = settings.orion_base_url
        self.service = settings.fiware_service
        self.service_path = settings.fiware_service_path
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    def _headers(self) -> Dict[str, str]:
        """Common headers for NGSI-LD requests"""
        return {
            "Content-Type": "application/ld+json",
            "FIWARE-Service": self.service,
            "FIWARE-ServicePath": self.service_path,
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Orion-LD"""
        url = f"{self.base_url}/{endpoint}"
        headers = self._headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params,
                )
                response.raise_for_status()
                if response.status_code == 204:
                    return {"status": "success"}
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Orion-LD request failed: {e}")
            raise

    async def query_entities(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        filters: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Query entities from Orion-LD.
        Supports type filtering, ID lookup, and NGSI-LD filters.
        """
        params = {"limit": limit, "offset": offset}

        if entity_type:
            params["type"] = entity_type
        if entity_id:
            params["id"] = entity_id
        if filters:
            params["q"] = filters

        result = await self._request("GET", "ngsi-ld/v1/entities", params=params)
        return result if isinstance(result, list) else [result]

    async def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """Get a single entity by ID"""
        result = await self._request("GET", f"ngsi-ld/v1/entities/{entity_id}")
        return result

    async def create_entity(self, entity: Dict[str, Any]) -> str:
        """Create a new entity in Orion-LD. Returns entity ID."""
        result = await self._request("POST", "ngsi-ld/v1/entities", json_data=entity)
        return result.get("id", entity.get("id", ""))

    async def update_entity(
        self, entity_id: str, entity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update entity attributes (PATCH)"""
        result = await self._request(
            "PATCH", f"ngsi-ld/v1/entities/{entity_id}/attrs", json_data=entity_data
        )
        return result

    async def upsert_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert entity (create if not exists, update if exists)"""
        entity_id = entity.get("id")
        try:
            # Try to get existing
            await self.get_entity(entity_id)
            # If exists, update
            entity_data = {k: v for k, v in entity.items() if k != "id"}
            return await self.update_entity(entity_id, entity_data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Doesn't exist, create new
                return await self.create_entity(entity)
            raise

    async def delete_entity(self, entity_id: str) -> Dict[str, Any]:
        """Delete an entity"""
        result = await self._request("DELETE", f"ngsi-ld/v1/entities/{entity_id}")
        return result

    async def query_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """Query all entities of a specific type"""
        return await self.query_entities(entity_type=entity_type, limit=1000)

    async def query_by_relationship(
        self, entity_id: str, relationship_name: str
    ) -> List[Dict[str, Any]]:
        """Query entities related to another entity"""
        # NGSI-LD relationship filter
        filter_str = f"hasRelationship({relationship_name})"
        return await self.query_entities(filters=filter_str, limit=1000)

    async def health_check(self) -> bool:
        """Check if Orion-LD is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/ngsi-ld/v1/entities", limit=1)
                return response.status_code in [200, 206]
        except Exception as e:
            logger.error(f"Orion-LD health check failed: {e}")
            return False


# Singleton instance
orion_client = OrionLDClient()
