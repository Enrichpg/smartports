# QuantumLeap Service Integration
# Handles all communication with QuantumLeap time-series manager

from typing import Dict, Any, Optional, List
import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)


class QuantumLeapService:
    """Service for interacting with QuantumLeap time-series manager"""

    def __init__(self):
        self.base_url = settings.quantumleap_base_url
        self.headers = {
            "FIWARE-Service": settings.fiware_service,
            "FIWARE-ServicePath": settings.fiware_service_path,
        }

    async def get_timeseries(
        self,
        entity_id: str,
        attribute: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get time-series data for an entity"""
        try:
            async with httpx.AsyncClient() as client:
                params = {"limit": limit}
                if attribute:
                    params["attr"] = attribute
                if from_date:
                    params["fromDate"] = from_date
                if to_date:
                    params["toDate"] = to_date

                response = await client.get(
                    f"{self.base_url}/v2/entities/{entity_id}",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching timeseries from QuantumLeap: {e}")
            raise

    async def query_timeseries(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        """Execute custom time-series query"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v2/timeseries/query",
                    json={"query": query},
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error executing QuantumLeap query: {e}")
            raise

    async def get_version(self) -> Dict[str, Any]:
        """Get QuantumLeap version info"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v2/version",
                    timeout=5.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching QuantumLeap version: {e}")
            raise


# Singleton instance
quantumleap_service = QuantumLeapService()
