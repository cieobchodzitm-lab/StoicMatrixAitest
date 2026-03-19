"""Embedding client — interface to the L2 LLM layer for generating embeddings."""
from __future__ import annotations

import logging
import math
from typing import List

logger = logging.getLogger(__name__)


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Return cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class EmbeddingClient:
    """Generates text embeddings by calling the Ollama /api/embeddings endpoint.

    .. note::
        In tests the ``_embed_fn`` hook is injected so no running Ollama
        instance is required.
    """

    def __init__(self, base_url: str, model: str = "nomic-embed-text", _embed_fn=None):
        self._base_url = base_url.rstrip("/")
        self._model = model
        # Allows test injection of a deterministic embedding function
        self._embed_fn = _embed_fn

    def embed(self, text: str) -> List[float]:
        """Return the embedding vector for *text*.

        Uses the injected ``_embed_fn`` when available; otherwise makes an
        HTTP POST to the Ollama embedding endpoint.
        """
        if self._embed_fn is not None:
            return self._embed_fn(text)

        try:
            import httpx  # noqa: PLC0415

            url = f"{self._base_url}/api/embeddings"
            response = httpx.post(
                url,
                json={"model": self._model, "prompt": text},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception:
            logger.exception("Failed to generate embedding for text=%r", text[:80])
            raise

    def similarity(self, a: List[float], b: List[float]) -> float:
        """Cosine similarity between two embedding vectors."""
        return _cosine_similarity(a, b)
