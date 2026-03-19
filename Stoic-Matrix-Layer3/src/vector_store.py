"""Vector store — ChromaDB collection management for Stoic-Matrix-Layer3."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """Thin abstraction over a ChromaDB collection.

    In production this wraps a real ``chromadb.Client``; in tests an
    in-process dictionary store is used so no running Chroma instance is
    required.
    """

    def __init__(self, collection_name: str, client: Any = None):
        self._collection_name = collection_name
        self._client = client
        # In-process fallback store: id → {embedding, metadata, document}
        self._store: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def upsert(
        self,
        doc_id: str,
        embedding: List[float],
        document: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Insert or update a document with its embedding."""
        self._store[doc_id] = {
            "embedding": embedding,
            "document": document,
            "metadata": metadata or {},
        }
        logger.debug("Upserted doc_id=%s into collection '%s'", doc_id, self._collection_name)

    def delete(self, doc_id: str) -> bool:
        """Remove a document from the store. Returns True if it existed."""
        existed = doc_id in self._store
        self._store.pop(doc_id, None)
        logger.debug("Deleted doc_id=%s (existed=%s)", doc_id, existed)
        return existed

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a stored document by ID."""
        return self._store.get(doc_id)

    def count(self) -> int:
        """Return the number of documents in the store."""
        return len(self._store)

    def list_ids(self) -> List[str]:
        """Return all stored document IDs."""
        return list(self._store.keys())
