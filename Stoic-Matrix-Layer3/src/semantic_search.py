"""Semantic search — nearest-neighbour retrieval over the vector store."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from .embedding_client import EmbeddingClient
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class SemanticSearch:
    """Wraps a VectorStore and EmbeddingClient to answer similarity queries."""

    def __init__(self, store: VectorStore, embedder: EmbeddingClient):
        self._store = store
        self._embedder = embedder

    def index(self, doc_id: str, text: str, metadata: Dict[str, Any] | None = None) -> None:
        """Embed *text* and store it under *doc_id*."""
        embedding = self._embedder.embed(text)
        self._store.upsert(doc_id=doc_id, embedding=embedding, document=text, metadata=metadata)
        logger.debug("Indexed doc_id=%s", doc_id)

    def query(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return the *top_k* most similar documents for the given *text*.

        Results are ordered by descending cosine similarity.
        """
        query_embedding = self._embedder.embed(text)
        results = []
        for doc_id in self._store.list_ids():
            entry = self._store.get(doc_id)
            if entry is None:
                continue
            score = self._embedder.similarity(query_embedding, entry["embedding"])
            results.append(
                {
                    "id": doc_id,
                    "score": score,
                    "document": entry["document"],
                    "metadata": entry["metadata"],
                }
            )
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]
