"""Memory manager — long-term and working memory for Stoic-Matrix-Layer3."""
from __future__ import annotations

import logging
from collections import deque
from typing import Any, Deque, Dict, List, Optional

logger = logging.getLogger(__name__)


class MemoryManager:
    """Manages short-term (working) memory and delegates long-term storage
    to the SemanticSearch / VectorStore components.

    Short-term memory is a bounded FIFO queue (capacity configurable).
    Long-term memory is represented by the injected ``long_term_store``
    object, which must expose ``index(doc_id, text, metadata)`` and
    ``query(text, top_k)`` (i.e. a :class:`SemanticSearch` instance).
    """

    def __init__(self, short_term_capacity: int = 100, long_term_store: Any = None):
        self._capacity = short_term_capacity
        self._working: Deque[Dict[str, Any]] = deque(maxlen=short_term_capacity)
        self._long_term = long_term_store

    # ------------------------------------------------------------------
    # Short-term (working) memory
    # ------------------------------------------------------------------

    def remember(self, record: Dict[str, Any]) -> None:
        """Add a record to working memory."""
        self._working.append(record)
        logger.debug("Working memory size: %d / %d", len(self._working), self._capacity)

    def recall_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Return the *n* most recently remembered records."""
        items = list(self._working)
        return items[-n:] if n < len(items) else items

    def clear_working_memory(self) -> None:
        """Discard all records in working memory."""
        self._working.clear()

    def working_memory_size(self) -> int:
        return len(self._working)

    # ------------------------------------------------------------------
    # Long-term memory (delegates to SemanticSearch)
    # ------------------------------------------------------------------

    def store_long_term(
        self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Persist a document to long-term vector memory."""
        if self._long_term is None:
            logger.warning("No long-term store configured; skipping store for doc_id=%s", doc_id)
            return
        self._long_term.index(doc_id, text, metadata)

    def search_long_term(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve semantically similar documents from long-term memory."""
        if self._long_term is None:
            logger.warning("No long-term store configured; returning empty results")
            return []
        return self._long_term.query(query, top_k=top_k)
