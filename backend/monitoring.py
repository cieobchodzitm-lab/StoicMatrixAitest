# backend/monitoring.py
# 📊 Prometheus Metrics & Performance Monitoring

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import time
from functools import wraps
import logging
from typing import Callable

logger = logging.getLogger(__name__)

# Custom registry
registry = CollectorRegistry()

# ========================
# METRICS DEFINITIONS
# ========================

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
    registry=registry
)

# Database metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=registry
)

db_query_errors_total = Counter(
    'db_query_errors_total',
    'Total database query errors',
    ['query_type', 'error_type'],
    registry=registry
)

db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Database connection pool size',
    registry=registry
)

db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections',
    registry=registry
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type'],
    registry=registry
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type'],
    registry=registry
)

cache_memory_usage_bytes = Gauge(
    'cache_memory_usage_bytes',
    'Cache memory usage in bytes',
    registry=registry
)

# Application metrics
active_users = Gauge(
    'active_users',
    'Number of active users',
    registry=registry
)

api_errors_total = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type'],
    registry=registry
)

# ========================
# DECORATORS
# ========================

def track_request(method: str, endpoint: str):
    """Track HTTP request metrics"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 500
            
            try:
                result = await func(*args, **kwargs)
                status_code = 200
                return result
            except Exception as e:
                status_code = 500
                api_errors_total.labels(
                    endpoint=endpoint,
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status_code
                ).inc()
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
        
        return wrapper
    return decorator

def track_db_query(query_type: str):
    """Track database query metrics"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                db_query_errors_total.labels(
                    query_type=query_type,
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(
                    query_type=query_type
                ).observe(duration)
        
        return wrapper
    return decorator

def update_pool_metrics(pool_stats: dict):
    """Update connection pool metrics"""
    db_connection_pool_size.set(pool_stats.get('pool_size', 0))
    db_connections_active.set(pool_stats.get('checked_out', 0))

def update_cache_metrics(cache_stats: dict):
    """Update cache metrics"""
    cache_memory_usage_bytes.set(
        cache_stats.get('used_memory_mb', 0) * 1024 * 1024
    )
