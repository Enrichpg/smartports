"""
Redis cache service.
Provides caching for frequently accessed data.
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Async Redis cache service.
    Handles all caching operations with reasonable defaults and fallback behavior.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
        self.default_ttl = 300  # 5 minutes default
    
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.client = await redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            await self.client.ping()
            logger.info(f"Connected to Redis: {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")
    
    def _is_available(self) -> bool:
        """Check if Redis is available."""
        return self.client is not None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (None = use default)
        
        Returns:
            True if successful, False if cache unavailable
        """
        
        if not self._is_available():
            logger.debug(f"Redis unavailable, skipping set for key: {key}")
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value) if not isinstance(value, str) else value
            await self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (ttl: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache for {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value if found, None if not found or cache unavailable
        """
        
        if not self._is_available():
            logger.debug(f"Redis unavailable, skipping get for key: {key}")
            return None
        
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            
            # Try to deserialize as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # If not JSON, return as is
                return value
        
        except Exception as e:
            logger.error(f"Error getting cache for {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self._is_available():
            return False
        
        try:
            await self.client.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache for {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        Useful for invalidating groups of cache entries.
        
        Args:
            pattern: Redis pattern (e.g., "port:*" to delete all port caches)
        
        Returns:
            Number of keys deleted
        """
        
        if not self._is_available():
            return 0
        
        try:
            keys = await self.client.keys(pattern)
            if keys:
                deleted = await self.client.delete(*keys)
                logger.debug(f"Cache pattern deleted: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error deleting cache pattern {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self._is_available():
            return False
        
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache existence for {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value in cache."""
        if not self._is_available():
            return None
        
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache for {key}: {e}")
            return None
    
    async def get_ttl(self, key: str) -> int:
        """Get remaining TTL for a key in seconds. -1 if no expiry, -2 if not found."""
        if not self._is_available():
            return -2
        
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for {key}: {e}")
            return -2
    
    async def health(self) -> Dict[str, Any]:
        """Get health status of Redis cache."""
        if not self._is_available():
            return {
                "status": "unavailable",
                "connected": False,
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        try:
            info = await self.client.info("memory")
            return {
                "status": "healthy",
                "connected": True,
                "memory_used_mb": info.get("used_memory", 0) / 1024 / 1024,
                "memory_max_mb": info.get("maxmemory", 0) / 1024 / 1024,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting Redis health: {e}")
            return {
                "status": "error",
                "connected": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Common cache key patterns
class CacheKeys:
    """Centralized cache key naming."""
    
    @staticmethod
    def port_summary(port_id: str) -> str:
        return f"port:summary:{port_id}"
    
    @staticmethod
    def port_availability(port_id: str) -> str:
        return f"port:availability:{port_id}"
    
    @staticmethod
    def port_alerts(port_id: str) -> str:
        return f"port:alerts:active:{port_id}"
    
    @staticmethod
    def dashboard_overview() -> str:
        return "dashboard:galicia:overview"
    
    @staticmethod
    def port_berths(port_id: str) -> str:
        return f"port:berths:{port_id}"
    
    @staticmethod
    def port_pattern(port_id: str) -> str:
        """Pattern to match all cache keys for a port."""
        return f"port:{port_id}:*"
    
    @staticmethod
    def global_pattern() -> str:
        """Pattern to match all port/global cache keys."""
        return "port:*"


# Global instance
_cache_instance: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Get or create the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance


def set_cache(cache: RedisCache) -> None:
    """Set the global cache instance."""
    global _cache_instance
    _cache_instance = cache
