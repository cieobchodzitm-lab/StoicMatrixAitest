"""Protocol bridge — HTTP ↔ Solana transaction translation for Layer4."""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ProtocolBridge:
    """Translates CNOTA virtue events into Solana transaction payloads."""

    def __init__(self, rpc_url: str, commitment: str = "confirmed"):
        self._rpc_url = rpc_url
        self._commitment = commitment

    def virtue_event_to_tx(self, user_id: str, virtues: Dict[str, int]) -> Dict[str, Any]:
        """Build a Solana-compatible transaction payload from a virtue score update."""
        total = sum(virtues.values())
        return {
            "jsonrpc": "2.0",
            "method": "sendTransaction",
            "params": [
                {
                    "user_id": user_id,
                    "virtues": virtues,
                    "total_score": total,
                    "commitment": self._commitment,
                }
            ],
            "id": 1,
        }

    def parse_tx_result(self, result: Dict[str, Any]) -> str:
        """Extract transaction signature from an RPC response."""
        return result.get("result", "")
