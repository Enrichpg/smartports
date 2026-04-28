# Base Connector Class
# Abstract base for all external API connectors

import httpx
import logging
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Base class for all external API connectors"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.source_name = self.__class__.__name__
        
    async def fetch(
        self, 
        endpoint: str, 
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch data from API with retry logic and error handling.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response data as dict with metadata about request
        """
        url = f"{self.base_url}{endpoint}"
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method,
                        url,
                        params=params,
                        headers=headers or {},
                    )
                    response.raise_for_status()
                    
                    return {
                        "status": "success",
                        "source": self.source_name,
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": response.json(),
                        "status_code": response.status_code,
                    }
                    
            except httpx.TimeoutException as e:
                logger.warning(f"{self.source_name}: Timeout on {endpoint} (attempt {retry_count + 1})")
                retry_count += 1
                if retry_count < self.max_retries:
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"{self.source_name}: HTTP {e.response.status_code} on {endpoint}")
                return {
                    "status": "error",
                    "source": self.source_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": f"HTTP {e.response.status_code}",
                    "status_code": e.response.status_code,
                }
                
            except Exception as e:
                logger.error(f"{self.source_name}: Error on {endpoint}: {str(e)}")
                retry_count += 1
                if retry_count < self.max_retries:
                    await asyncio.sleep(2 ** retry_count)
        
        return {
            "status": "error",
            "source": self.source_name,
            "timestamp": datetime.utcnow().isoformat(),
            "error": f"Failed after {self.max_retries} attempts",
        }
    
    @abstractmethod
    async def get_weather_data(self, location: str) -> Dict[str, Any]:
        """Get weather data for a location"""
        pass
    
    @abstractmethod
    async def normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize API response to common format"""
        pass
