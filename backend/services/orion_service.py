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
        options: str = "keyValues,upsert"
    ) -> Dict[str, Any]:
        """Upsert NGSI-LD entity (create if not exists, update if exists)"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/ngsi-ld/v1/entities"
                
                logger.info(f"Upserting entity {entity.get('id')}")
                
                response = await client.post(
                    url,
                    json=entity,
                    headers=self.headers,
                    params={"options": options}
                )
                
                if response.status_code in [201, 204, 200]:
                    logger.info(f"Entity {entity.get('id')} upserted successfully")
                    return {"success": True, "id": entity.get('id'), "status": response.status_code}
                else:
                    logger.error(f"Error upserting entity: {response.status_code} - {response.text}")
                    return {"success": False, "status": response.status_code, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Exception upserting entity: {e}")
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
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Batch upsert multiple entities with dry-run capability"""
        results = {
            "total": len(entities),
            "successful": 0,
            "failed": 0,
            "dry_run": dry_run,
            "details": []
        }
        
        for entity in entities:
            if dry_run:
                logger.info(f"[DRY-RUN] Would upsert {entity.get('id')}")
                results["details"].append({
                    "id": entity.get('id'),
                    "status": "dry-run"
                })
            else:
                result = await self.upsert_entity(entity)
                if result.get("success"):
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                results["details"].append(result)
        
        logger.info(f"Batch upsert completed: {results['successful']} successful, {results['failed']} failed")
        return results
