"""NFT Passport router."""
import uuid
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


def _mock_passport(user_id: str) -> dict:
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
    """Return passport data for a user."""
    return _mock_passport(user_id)


class MintRequest(BaseModel):
    user_id: str


@router.post("/api/passport/mint")
async def mint_passport(request: MintRequest):
    """Queue an ERC-1155 passport mint."""
    tx_id = f"tx_{uuid.uuid4().hex[:16]}"
    return {
        "status": "queued",
        "tx_id": tx_id,
        "user_id": request.user_id,
        "message": "Mint queued for processing on Solana L7 Bridge",
    }
