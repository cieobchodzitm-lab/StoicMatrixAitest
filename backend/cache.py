# backend/cache.py
# 💾 Redis Caching Layer with TTL Management

import redis
import json
from functools import wraps
from typing import Any, Callable, Optional
import logging
from datetime import timedelta
import hashlib

logger = logging.getLogger(__name__)

class CacheManager:
    """Centralized cache management"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 minutes
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache error on GET: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache error on SET: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache error on DELETE: {e}")
            return False
    
    def flush_pattern(self, pattern: str) -> int:
        """Flush all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            logger.debug(f"Cache FLUSH: {pattern} ({len(keys)} keys)")
            return len(keys)
        except Exception as e:
            logger.error(f"Cache error on FLUSH: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                "used_memory_mb": info.get('used_memory', 0) / 1024 / 1024,
                "connected_clients": info.get('connected_clients', 0),
                "total_commands": info.get('total_commands_processed', 0)
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {}

# Global cache instance
cache_manager = None

def init_cache(redis_url: str):
    """Initialize cache manager"""
    global cache_manager
    cache_manager = CacheManager(redis_url)
    logger.info("✅ Cache manager initialized")

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function args"""
    key_parts = [str(arg) for arg in args] + [
        f"{k}={v}" for k, v in sorted(kwargs.items())
    ]
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if cache_manager is None:
                return await func(*args, **kwargs)
            
            cache_id = f"{key_prefix or func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_id)
            if cached_value is not None:
                logger.debug(f"🎯 Returning cached result for {func.__name__}")
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_id, result, ttl)
            return result
        
        return async_wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Invalidate cache by pattern"""
    if cache_manager:
        cache_manager.flush_pattern(pattern)
        logger.info(f"🗑️ Cache invalidated: {pattern}")
