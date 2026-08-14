"""NFT Passport router — now gated by Virtue Passport verification."""
from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.passport_bridge import (
    VerificationResult,
    prepare_mint_payload,
    verify_passport,
)

router = APIRouter()

# Optional: load a trusted public key for production verification
# (set PASSPORT_PUBLIC_KEY_PEM env or path)
_PUBLIC_KEY_PEM: Optional[str] = os.getenv("PASSPORT_PUBLIC_KEY_PEM")


def _mock_passport(user_id: str) -> dict:
    """Fallback demo data when no signed passport is supplied."""
    import random

    rng = random.Random(user_id)
    token_num = rng.randint(1, 9999)
    sophia = rng.randint(55, 99)
    andreia = rng.randint(50, 99)
    dikaiosyne = rng.randint(55, 99)
    sophrosyne = rng.randint(50, 99)
    return {
        "token_id": f"L7-NFT-{token_num:04d}",
        "user_id": user_id,
        "display_name": f"Citizen {user_id}",
        "virtues": {
            "sophia": sophia,
            "andreia": andreia,
            "dikaiosyne": dikaiosyne,
            "sophrosyne": sophrosyne,
        },
        "total_score": sophia + andreia + dikaiosyne + sophrosyne,
        "rank": rng.randint(1, 100),
        "created_at": datetime(2024, 1, 15, 10, 30).isoformat() + "Z",
        "source": "mock",
    }


@router.get("/api/passport/{user_id}/metadata")
async def get_passport_metadata(user_id: str):
    """Return ERC-1155 metadata JSON for a passport."""
    passport = _mock_passport(user_id)
    virtues = passport["virtues"]
    return {
        "name": f"L7 Virtue Passport — {user_id}",
        "description": "Stoic virtue governance passport on the L7 Rzeczpospolita network.",
        "image": "https://huggingface.co/spaces/cieobchodzitm/l7-cnota-dashboard/resolve/main/passport.png",
        "attributes": [
            {"trait_type": "Sophia (Wisdom)", "value": virtues["sophia"]},
            {"trait_type": "Andreia (Courage)", "value": virtues["andreia"]},
            {"trait_type": "Dikaiosyne (Justice)", "value": virtues["dikaiosyne"]},
            {"trait_type": "Sophrosyne (Temperance)", "value": virtues["sophrosyne"]},
            {"trait_type": "Total Score", "value": passport["total_score"]},
            {"trait_type": "Rank", "value": passport["rank"]},
        ],
        "token_id": passport["token_id"],
    }


@router.get("/api/passport/{user_id}")
async def get_passport(user_id: str):
    """Return passport data for a user (mock until on-chain index is wired)."""
    return _mock_passport(user_id)


class MintRequest(BaseModel):
    user_id: str
    signed_passport: Optional[Dict[str, Any]] = Field(
        None,
        description="Signed AGT-VIRTUE-PASSPORT-v1 object from phantom-crypto-core",
    )
    virtue_scores: Optional[Dict[str, int]] = Field(
        None,
        description="Optional override of the four cardinal virtues",
    )


@router.post("/api/passport/mint")
async def mint_passport(request: MintRequest):
    """
    Queue an ERC-1155 / Solana Virtue Passport mint.

    Production path:
      - signed_passport must be present and verify as TRUSTED
      - then prepare_mint_payload → real Anchor call (the-bridge-virtue-nft)

    Demo path (no signed_passport):
      - falls back to mock queue (backward compatible)
    """
    tx_id = f"tx_{uuid.uuid4().hex[:16]}"

    # --- Production verification path ---
    if request.signed_passport:
        result: VerificationResult = verify_passport(
            request.signed_passport,
            public_key_pem=_PUBLIC_KEY_PEM,
            require_trusted=True,
        )
        if not result.valid:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "passport_verification_failed",
                    "reason": result.reason,
                    "agent_class": result.agent_class,
                },
            )

        scores = request.virtue_scores or {
            "sophia": 80,
            "andreia": 75,
            "dikaiosyne": 85,
            "sophrosyne": 78,
        }
        payload = prepare_mint_payload(result, request.user_id, scores)

        # TODO: real Solana RPC call using solana-py / anchorpy
        # when PASSPORT_RPC_URL + keypair are configured.
        # For now we return the prepared payload so the frontend / operator
        # can see that the cryptographic gate passed.
        return {
            "status": "verified_and_queued",
            "tx_id": tx_id,
            "user_id": request.user_id,
            "verification": {
                "agent_class": result.agent_class,
                "constitution_id": result.constitution_id,
                "scope": result.scope,
                "note": result.note,
            },
            "mint_payload": payload,
            "message": (
                "Passport verified as TRUSTED. "
                "Mint payload prepared for the-bridge-virtue-nft. "
                "On-chain submission pending RPC credentials."
            ),
        }

    # --- Demo / backward-compatible path ---
    return {
        "status": "queued",
        "tx_id": tx_id,
        "user_id": request.user_id,
        "message": "Mint queued for processing on Solana L7 Bridge (demo mode — no signed passport supplied)",
    }
