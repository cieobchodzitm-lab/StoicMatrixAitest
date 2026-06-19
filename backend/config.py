# backend/config.py
# 🔧 Database Configuration with Connection Pooling & Optimization

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from contextlib import contextmanager
import os
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/stoic"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 🚀 Connection Pool Configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,                    # Active connections in pool
    max_overflow=40,                 # Additional temporary connections
    pool_pre_ping=True,              # Verify connections before use
    pool_recycle=3600,               # Recycle connections every hour
    pool_reset_on_return='rollback', # Reset connection state
    echo=DEBUG,                      # Log SQL queries (only in debug)
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"  # 30s statement timeout
    }
)

# Event listeners for connection management
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Configure connection on creation"""
    dbapi_connection.isolation_level = 'READ_COMMITTED'
    logger.debug("Database connection created")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection return to pool"""
    logger.debug("Connection returned to pool")

# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent lazy loading after commit
)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Database session context manager"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

# 📊 Pool Statistics
def get_pool_stats():
    """Get connection pool statistics"""
    pool = engine.pool
    return {
        "pool_size": pool.pool_size,
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.size() + pool.overflow()
    }
