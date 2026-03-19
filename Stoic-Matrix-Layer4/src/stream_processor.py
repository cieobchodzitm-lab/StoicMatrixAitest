"""Stream processor — activity data buffering and batching for Layer4."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, List, Optional

logger = logging.getLogger(__name__)


class StreamProcessor:
    """Buffers incoming activity records and flushes them in batches."""

    def __init__(
        self,
        batch_size: int = 50,
        flush_interval_sec: float = 5.0,
        on_flush: Optional[Callable[[List[Any]], None]] = None,
    ):
        self._batch_size = batch_size
        self._flush_interval = flush_interval_sec
        self._on_flush = on_flush or (lambda batch: None)
        self._buffer: List[Any] = []

    def ingest(self, record: Any) -> None:
        """Add a record to the buffer. Flushes immediately if batch is full."""
        self._buffer.append(record)
        logger.debug("Buffer size: %d / %d", len(self._buffer), self._batch_size)
        if len(self._buffer) >= self._batch_size:
            self.flush()

    def flush(self) -> List[Any]:
        """Drain the buffer and invoke the flush callback."""
        batch = self._buffer[:]
        self._buffer.clear()
        if batch:
            logger.info("Flushing batch of %d records", len(batch))
            self._on_flush(batch)
        return batch

    async def run(self) -> None:
        """Periodically flush the buffer on a timer.

        The loop exits when the task is cancelled (e.g. via
        ``task.cancel()``), which raises ``asyncio.CancelledError`` and
        causes a final flush before propagating the exception.
        """
        try:
            while True:
                await asyncio.sleep(self._flush_interval)
                self.flush()
        except asyncio.CancelledError:
            self.flush()  # drain remaining records before shutting down
            raise
