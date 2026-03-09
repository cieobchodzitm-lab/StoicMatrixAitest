"""CNOTA virtue scoring router."""
import random
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

MOCK_NAMES = [
    "Marcus Aurelius", "Epictetus", "Seneca", "Cato the Elder", "Zeno of Citium",
    "Cleanthes", "Chrysippus", "Musonius Rufus", "Cicero", "Scipio Africanus",
]


def _mock_virtues(seed: str) -> dict:
    rng = random.Random(seed)
    sophia = rng.randint(55, 99)
    andreia = rng.randint(50, 99)
    dikaiosyne = rng.randint(55, 99)
    sophrosyne = rng.randint(50, 99)
    return {
        "sophia": sophia,
        "andreia": andreia,
        "dikaiosyne": dikaiosyne,
        "sophrosyne": sophrosyne,
        "total_score": sophia + andreia + dikaiosyne + sophrosyne,
    }


@router.get("/api/cnota/profile/{user_id}")
async def get_profile(user_id: str):
    """Return virtue profile for a user."""
    virtues = _mock_virtues(user_id)
    idx = abs(hash(user_id)) % len(MOCK_NAMES)
    return {
        "user_id": user_id,
        "display_name": MOCK_NAMES[idx],
        "rank": (abs(hash(user_id)) % 100) + 1,
        **virtues,
    }


@router.get("/api/cnota/leaderboard")
async def get_leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Return top users by virtue score."""
    entries = []
    for i in range(100):
        uid = f"user_{i + 1:03d}"
        virtues = _mock_virtues(uid)
        entries.append({
            "rank": i + 1,
            "user_id": uid,
            "display_name": MOCK_NAMES[i % len(MOCK_NAMES)],
            **virtues,
            "virtues": {
                "sophia": virtues["sophia"],
                "andreia": virtues["andreia"],
                "dikaiosyne": virtues["dikaiosyne"],
                "sophrosyne": virtues["sophrosyne"],
            },
        })
    entries.sort(key=lambda x: x["total_score"], reverse=True)
    for rank, entry in enumerate(entries, start=1):
        entry["rank"] = rank
    page = entries[offset: offset + limit]
    return {"entries": page, "total": len(entries), "limit": limit, "offset": offset}


class ScoreRequest(BaseModel):
    user_id: str
    activity_data: dict = {}


@router.post("/api/cnota/score")
async def calculate_score(request: ScoreRequest):
    """Calculate virtue score from on-chain activity."""
    virtues = _mock_virtues(request.user_id)
    return {"user_id": request.user_id, **virtues, "status": "calculated"}


@router.get("/api/cnota/stats")
async def get_stats():
    """Return aggregate virtue statistics."""
    return {
        "total_users": 100,
        "average_score": 285,
        "top_virtue": "dikaiosyne",
        "passports_minted": 42,
    }
