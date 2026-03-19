"""Tests for Stoic-Matrix-Layer4 components."""
import asyncio

import pytest

from src.event_bus import Event, InMemoryEventBus
from src.persistence import PersistenceClient
from src.protocol_bridge import ProtocolBridge
from src.stream_processor import StreamProcessor


# ---------------------------------------------------------------------------
# InMemoryEventBus
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    bus = InMemoryEventBus()
    received: list = []

    async def virtue_update_handler(event: Event):
        received.append(event)

    bus.subscribe("virtue.updated", virtue_update_handler)
    await bus.publish(Event(stream="virtue.updated", payload={"user_id": "u1", "total_score": 300}))

    assert len(received) == 1
    assert received[0].payload["user_id"] == "u1"


@pytest.mark.asyncio
async def test_event_bus_no_subscribers():
    bus = InMemoryEventBus()
    # Should not raise even without subscribers
    await bus.publish(Event(stream="unknown.stream", payload={}))


# ---------------------------------------------------------------------------
# PersistenceClient
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_persistence_store_and_fetch():
    client = PersistenceClient(db_url="postgresql://localhost/test")
    await client.store("user:001", {"sophia": 80, "andreia": 75})
    result = await client.fetch("user:001")
    assert result == {"sophia": 80, "andreia": 75}


@pytest.mark.asyncio
async def test_persistence_fetch_missing_returns_none():
    client = PersistenceClient(db_url="postgresql://localhost/test")
    result = await client.fetch("does_not_exist")
    assert result is None


@pytest.mark.asyncio
async def test_persistence_delete():
    client = PersistenceClient(db_url="postgresql://localhost/test")
    await client.store("key1", {"x": 1})
    deleted = await client.delete("key1")
    assert deleted is True
    assert await client.fetch("key1") is None


# ---------------------------------------------------------------------------
# ProtocolBridge
# ---------------------------------------------------------------------------

def test_protocol_bridge_virtue_event_to_tx():
    bridge = ProtocolBridge(rpc_url="http://localhost:8899")
    tx = bridge.virtue_event_to_tx(
        user_id="user_001",
        virtues={"sophia": 80, "andreia": 75, "dikaiosyne": 90, "sophrosyne": 70},
    )
    assert tx["method"] == "sendTransaction"
    assert tx["params"][0]["total_score"] == 315


def test_protocol_bridge_parse_tx_result():
    bridge = ProtocolBridge(rpc_url="http://localhost:8899")
    sig = bridge.parse_tx_result({"result": "5Ry6xZyg"})
    assert sig == "5Ry6xZyg"


# ---------------------------------------------------------------------------
# StreamProcessor
# ---------------------------------------------------------------------------

def test_stream_processor_flush_on_batch_full():
    flushed = []
    proc = StreamProcessor(batch_size=3, on_flush=flushed.extend)
    proc.ingest({"id": 1})
    proc.ingest({"id": 2})
    assert flushed == []
    proc.ingest({"id": 3})  # triggers flush
    assert len(flushed) == 3


def test_stream_processor_manual_flush():
    flushed = []
    proc = StreamProcessor(batch_size=100, on_flush=flushed.extend)
    proc.ingest({"id": 1})
    proc.ingest({"id": 2})
    batch = proc.flush()
    assert len(batch) == 2
    assert flushed == [{"id": 1}, {"id": 2}]
    assert proc.flush() == []  # buffer is empty after flush
