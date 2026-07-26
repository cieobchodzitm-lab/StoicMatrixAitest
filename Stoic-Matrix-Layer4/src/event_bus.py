"""Event bus — inter-layer event routing for Stoic-Matrix-Layer4."""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class Event:
    stream: str
    payload: dict
    source: str = "layer4"


@dataclass
class InMemoryEventBus:
    """Simple in-process pub/sub bus (for testing and dev without Redis)."""

    _subscribers: Dict[str, List[Callable]] = field(default_factory=dict)

    def subscribe(self, stream: str, handler: Callable) -> None:
        self._subscribers.setdefault(stream, []).append(handler)
        logger.debug("Subscribed %s to stream '%s'", handler, stream)

    async def publish(self, event: Event) -> None:
        handlers = self._subscribers.get(event.stream, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception:
                logger.exception("Handler %s failed for event on stream '%s'", handler, event.stream)

    def to_json(self, event: Event) -> str:
        return json.dumps({"stream": event.stream, "source": event.source, "payload": event.payload})
