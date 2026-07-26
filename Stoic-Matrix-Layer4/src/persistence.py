"""Persistence bridge — write-through cache and DB storage for Layer4."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PersistenceClient:
    """Thin persistence interface used by higher layers."""

    def __init__(self, db_url: str):
        self._db_url = db_url
        self._cache: Dict[str, Any] = {}

    async def store(self, key: str, value: dict) -> None:
        """Write a record to the write-through cache and underlying DB.

        .. note::
            Database write-through (asyncpg/SQLAlchemy) is not yet
            implemented.  All data is currently held in the in-process
            cache and will be lost on restart.  Track progress in
            https://github.com/cieobchodzitm-lab/Stoic-Matrix-Layer4/issues
        """
        self._cache[key] = value
        logger.debug("Stored key=%s", key)

    async def fetch(self, key: str) -> Optional[dict]:
        """Retrieve a record (cache-first)."""
        if key in self._cache:
            return self._cache[key]
        logger.debug("Cache miss for key=%s — would fetch from DB", key)
        return None

    async def delete(self, key: str) -> bool:
        """Remove a record."""
        existed = key in self._cache
        self._cache.pop(key, None)
        return existed
