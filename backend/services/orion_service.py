# Orion-LD Service Integration - Improved
# Handles all communication with FIWARE Orion-LD context broker
# Includes create, update, upsert, query operations with proper error handling

from typing import Dict, Any, Optional, List
import httpx
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class OrionService:
    """Service for interacting with Orion-LD context broker"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        fiware_service: str = "smartport",
        fiware_service_path: str = "/galicia"
    ):
        """Initialize Orion service"""
        self.base_url = base_url or os.getenv("ORION_BASE_URL", "http://localhost:1026")
        self.fiware_service = fiware_service
        self.fiware_service_path = fiware_service_path
        
        self.headers = {
            "FIWARE-Service": fiware_service,
            "FIWARE-ServicePath": fiware_service_path,
            "Content-Type": "application/ld+json",
        }
    
    async def create_entity(
        self,
        entity: Dict[str, Any],
        options: str = "keyValues"
    ) -> Dict[str, Any]:
        """Create a new NGSI-LD entity in Orion"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/ngsi-ld/v1/entities"
                
                logger.info(f"Creating entity {entity.get('id')} in Orion")
                
                response = await client.post(
                    url,
                    json=entity,
                    headers=self.headers,
                    params={"options": options}
                )
                
                if response.status_code in [201, 204]:
                    logger.info(f"Entity {entity.get('id')} created successfully")
                    return {"success": True, "id": entity.get('id'), "status": response.status_code}
                else:
                    logger.error(f"Error creating entity: {response.status_code} - {response.text}")
                    return {"success": False, "status": response.status_code, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Exception creating entity: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_entity(
        self,
        entity_id: str,
        attrs: Dict[str, Any],
        options: str = "keyValues"
    ) -> Dict[str, Any]:
        """Update attributes of an existing NGSI-LD entity"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/ngsi-ld/v1/entities/{entity_id}/attrs"
                
                logger.info(f"Updating entity {entity_id}")
                
                response = await client.patch(
                    url,
                    json=attrs,
                    headers=self.headers,
                    params={"options": options}
                )
                
                if response.status_code in [204, 200]:
                    logger.info(f"Entity {entity_id} updated successfully")
                    return {"success": True, "id": entity_id, "status": response.status_code}
                else:
                    logger.error(f"Error updating entity: {response.status_code} - {response.text}")
                    return {"success": False, "status": response.status_code, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Exception updating entity: {e}")
            return {"success": False, "error": str(e)}
    
    async def upsert_entity(
        self,
        entity: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Upsert NGSI-LD entity: POST to create, PATCH attrs if 409 (already exists)."""
        entity_id = entity.get("id")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to create first
                create_resp = await client.post(
                    f"{self.base_url}/ngsi-ld/v1/entities",
                    json=entity,
                    headers=self.headers,
                )
                if create_resp.status_code in (201, 204):
                    return {"success": True, "id": entity_id, "status": create_resp.status_code}

                if create_resp.status_code == 409:
                    # Entity exists — patch its attributes
                    attrs = {k: v for k, v in entity.items() if k not in ("id", "type", "@context")}
                    patch_resp = await client.patch(
                        f"{self.base_url}/ngsi-ld/v1/entities/{entity_id}/attrs",
                        json=attrs,
                        headers=self.headers,
                    )
                    if patch_resp.status_code in (204, 207):
                        return {"success": True, "id": entity_id, "status": patch_resp.status_code}
                    logger.error("PATCH attrs %s: %s %s", entity_id, patch_resp.status_code, patch_resp.text)
                    return {"success": False, "status": patch_resp.status_code, "error": patch_resp.text}

                logger.error("POST entity %s: %s %s", entity_id, create_resp.status_code, create_resp.text)
                return {"success": False, "status": create_resp.status_code, "error": create_resp.text}

        except Exception as e:
            logger.error("Exception upserting entity %s: %s", entity_id, e)
            return {"success": False, "error": str(e)}
    
    async def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """Get a specific NGSI-LD entity"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/ngsi-ld/v1/entities/{entity_id}"
                
                response = await client.get(
                    url,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Entity {entity_id} retrieved")
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Entity {entity_id} not found")
                    return None
                else:
                    logger.error(f"Error retrieving entity: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Exception retrieving entity: {e}")
            return None
    
    async def get_entities(
        self,
        entity_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get NGSI-LD entities from Orion"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/ngsi-ld/v1/entities"
                
                params = {"limit": limit, "offset": offset}
                if entity_type:
                    params["type"] = entity_type
                
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Retrieved {len(result)} entities")
                    return result
                else:
                    logger.error(f"Error fetching entities: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Exception fetching entities: {e}")
            return []
    
    async def delete_entity(self, entity_id: str) -> Dict[str, Any]:
        """Delete an NGSI-LD entity"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/ngsi-ld/v1/entities/{entity_id}"
                
                logger.info(f"Deleting entity {entity_id}")
                
                response = await client.delete(
                    url,
                    headers=self.headers
                )
                
                if response.status_code == 204:
                    logger.info(f"Entity {entity_id} deleted successfully")
                    return {"success": True, "id": entity_id}
                else:
                    logger.error(f"Error deleting entity: {response.status_code}")
                    return {"success": False, "status": response.status_code}
                    
        except Exception as e:
            logger.error(f"Exception deleting entity: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_entities(
        self,
        q: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query entities with advanced filters"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/ngsi-ld/v1/entities"
                
                params = {"limit": limit}
                if q:
                    params["q"] = q
                if entity_type:
                    params["type"] = entity_type
                
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Error querying entities: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Exception querying entities: {e}")
            return []
    
    async def batch_upsert_entities(
        self,
        entities: List[Dict[str, Any]],
        dry_run: bool = False,
        chunk_size: int = 50,
    ) -> Dict[str, Any]:
        """
        Batch upsert using POST /ngsi-ld/v1/entityOperations/upsert (native NGSI-LD batch).
        Falls back to individual upsert_entity per entity on chunk failure.
        """
        results = {"total": len(entities), "successful": 0, "failed": 0, "dry_run": dry_run}

        if dry_run:
            for entity in entities:
                logger.info("[DRY-RUN] Would upsert %s", entity.get("id"))
            results["successful"] = len(entities)
            return results

        batch_url = f"{self.base_url}/ngsi-ld/v1/entityOperations/upsert"
        headers = {**self.headers, "Content-Type": "application/json"}

        for i in range(0, len(entities), chunk_size):
            chunk = entities[i:i + chunk_size]
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(batch_url, json=chunk, headers=headers)
                if resp.status_code in (204, 201):
                    results["successful"] += len(chunk)
                    logger.info("Batch chunk %d–%d: OK", i, i + len(chunk))
                else:
                    logger.warning(
                        "Batch chunk %d–%d failed (%s), falling back to individual upserts: %s",
                        i, i + len(chunk), resp.status_code, resp.text[:200],
                    )
                    for entity in chunk:
                        r = await self.upsert_entity(entity)
                        if r.get("success"):
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
            except Exception as e:
                logger.error("Batch chunk %d–%d exception: %s", i, i + len(chunk), e)
                results["failed"] += len(chunk)

        logger.info("Batch upsert completed: %d successful, %d failed", results["successful"], results["failed"])
        return results
