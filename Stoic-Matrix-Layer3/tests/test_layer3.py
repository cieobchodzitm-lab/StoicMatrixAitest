"""Tests for Stoic-Matrix-Layer3 components."""
import math

import pytest

from src.embedding_client import EmbeddingClient, _cosine_similarity
from src.memory_manager import MemoryManager
from src.semantic_search import SemanticSearch
from src.vector_store import VectorStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_embedder() -> EmbeddingClient:
    """Return an EmbeddingClient that uses a deterministic hash-based embed fn."""

    def _hash_embed(text: str):
        """Very simple deterministic 4-d embedding for testing."""
        h = hash(text)
        return [
            float((h >> 0) & 0xFF) / 255.0,
            float((h >> 8) & 0xFF) / 255.0,
            float((h >> 16) & 0xFF) / 255.0,
            float((h >> 24) & 0xFF) / 255.0,
        ]

    return EmbeddingClient(base_url="http://localhost:11434", _embed_fn=_hash_embed)


# ---------------------------------------------------------------------------
# _cosine_similarity
# ---------------------------------------------------------------------------

def test_cosine_similarity_identical():
    v = [1.0, 0.0, 0.0]
    assert _cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    assert _cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    assert _cosine_similarity([0.0, 0.0], [1.0, 2.0]) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# EmbeddingClient
# ---------------------------------------------------------------------------

def test_embedding_client_returns_list():
    client = _make_embedder()
    result = client.embed("sophia and andreia")
    assert isinstance(result, list)
    assert len(result) == 4


def test_embedding_client_deterministic():
    client = _make_embedder()
    assert client.embed("test text") == client.embed("test text")


def test_embedding_client_similarity():
    client = _make_embedder()
    v = client.embed("virtue")
    assert client.similarity(v, v) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# VectorStore
# ---------------------------------------------------------------------------

def test_vector_store_upsert_and_get():
    store = VectorStore(collection_name="test")
    store.upsert("doc1", [0.1, 0.2, 0.3], document="sophia", metadata={"layer": "L3"})
    result = store.get("doc1")
    assert result is not None
    assert result["document"] == "sophia"
    assert result["metadata"]["layer"] == "L3"


def test_vector_store_count():
    store = VectorStore(collection_name="test")
    assert store.count() == 0
    store.upsert("a", [1.0], document="alpha")
    store.upsert("b", [2.0], document="beta")
    assert store.count() == 2


def test_vector_store_delete():
    store = VectorStore(collection_name="test")
    store.upsert("x", [0.5], document="x-doc")
    assert store.delete("x") is True
    assert store.get("x") is None
    assert store.delete("x") is False


def test_vector_store_list_ids():
    store = VectorStore(collection_name="test")
    store.upsert("id1", [0.1])
    store.upsert("id2", [0.2])
    ids = store.list_ids()
    assert set(ids) == {"id1", "id2"}


# ---------------------------------------------------------------------------
# SemanticSearch
# ---------------------------------------------------------------------------

def test_semantic_search_index_and_query():
    store = VectorStore(collection_name="virtue-memory")
    embedder = _make_embedder()
    search = SemanticSearch(store=store, embedder=embedder)

    search.index("doc_sophia", "sophia is practical wisdom")
    search.index("doc_andreia", "andreia is courage and resilience")
    search.index("doc_dikaiosyne", "dikaiosyne is justice and fairness")

    results = search.query("wisdom and justice", top_k=2)
    assert len(results) == 2
    assert all("id" in r and "score" in r for r in results)
    # scores should be in descending order
    assert results[0]["score"] >= results[1]["score"]


def test_semantic_search_top_k_capped():
    store = VectorStore(collection_name="test")
    embedder = _make_embedder()
    search = SemanticSearch(store=store, embedder=embedder)
    for i in range(3):
        search.index(f"doc{i}", f"document number {i}")
    results = search.query("document", top_k=10)
    assert len(results) == 3  # only 3 exist


def test_semantic_search_empty_store():
    store = VectorStore(collection_name="empty")
    embedder = _make_embedder()
    search = SemanticSearch(store=store, embedder=embedder)
    assert search.query("anything") == []


# ---------------------------------------------------------------------------
# MemoryManager
# ---------------------------------------------------------------------------

def test_memory_manager_remember_and_recall():
    mgr = MemoryManager(short_term_capacity=5)
    for i in range(3):
        mgr.remember({"event": f"virtue_update_{i}"})
    recent = mgr.recall_recent(n=10)
    assert len(recent) == 3
    assert recent[-1]["event"] == "virtue_update_2"


def test_memory_manager_capacity_eviction():
    mgr = MemoryManager(short_term_capacity=3)
    for i in range(5):
        mgr.remember({"i": i})
    assert mgr.working_memory_size() == 3
    recent = mgr.recall_recent(n=3)
    assert recent[0]["i"] == 2  # oldest surviving record


def test_memory_manager_clear():
    mgr = MemoryManager()
    mgr.remember({"x": 1})
    mgr.clear_working_memory()
    assert mgr.working_memory_size() == 0


def test_memory_manager_long_term_store_and_search():
    store = VectorStore(collection_name="long-term")
    embedder = _make_embedder()
    search = SemanticSearch(store=store, embedder=embedder)
    mgr = MemoryManager(long_term_store=search)

    mgr.store_long_term("crisis_001", "flooding crisis in northern region", {"severity": "high"})
    mgr.store_long_term("virtue_001", "sophia score updated for user alpha", {"user": "alpha"})

    results = mgr.search_long_term("crisis flooding", top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == "crisis_001"


def test_memory_manager_long_term_no_store():
    mgr = MemoryManager()  # no long_term_store
    mgr.store_long_term("x", "text")  # should not raise
    assert mgr.search_long_term("text") == []
