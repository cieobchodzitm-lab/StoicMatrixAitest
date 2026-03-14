"""Rewards processor — virtue score to NFT mint pipeline."""
import uuid
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RewardRequest(BaseModel):
    user_id: str
    virtue_score: int
    activity_type: str = "governance_vote"


@router.post("/api/rewards/process")
async def process_reward(request: RewardRequest):
    """Process a virtue score event and queue an NFT mint via Solana L7 Bridge.

    Currently stubbed — returns queued status without actual on-chain call.
    """
    tx_id = f"tx_{uuid.uuid4().hex[:16]}"
    return {
        "status": "queued",
        "tx_id": tx_id,
        "user_id": request.user_id,
        "virtue_score": request.virtue_score,
        "activity_type": request.activity_type,
        "bridge": "solana_l7_rpc_stub",
    }


@router.get("/api/rewards/queue")
async def get_queue_status():
    """Return the current reward processing queue status."""
    return {
        "queued": 3,
        "processing": 1,
        "completed": 127,
        "failed": 0,
        "bridge_status": "mock",
    }
