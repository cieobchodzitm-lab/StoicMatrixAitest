"""mode: agent."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class VirtueLogCreateRequest(BaseModel):
    user_id: str
    action: str
    sophia: int = 0
    andreia: int = 0
    dikaiosyne: int = 0
    sophrosyne: int = 0


def _build_mock_log(entry_id: int) -> dict:
    base = 55 + (entry_id % 20)
    return {
        "id": f"log_{entry_id:03d}",
        "user_id": f"user_{(entry_id % 12) + 1:03d}",
        "action": "governance_vote" if entry_id % 2 == 0 else "community_review",
        "virtues": {
            "sophia": base,
            "andreia": base - 2,
            "dikaiosyne": base + 3,
            "sophrosyne": base - 1,
        },
        "total_score": (base * 4),
        "created_at": (
            datetime.now(timezone.utc) - timedelta(hours=entry_id)
        ).isoformat(),
    }


@router.get("/api/virtue_log/list")
async def list_virtue_logs(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Return paginated virtue log entries."""
    logs = [_build_mock_log(i + 1) for i in range(60)]
    page = logs[offset: offset + limit]
    return {"entries": page, "total": len(logs), "limit": limit, "offset": offset}


@router.get("/api/virtue_log/{user_id}")
async def get_user_virtue_log(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Return paginated virtue log entries for a specific user."""
    user_logs = []
    for i in range(30):
        entry = _build_mock_log(i + 1)
        entry["user_id"] = user_id
        user_logs.append(entry)

    page = user_logs[offset: offset + limit]
    return {
        "user_id": user_id,
        "entries": page,
        "total": len(user_logs),
        "limit": limit,
        "offset": offset,
    }


@router.post("/api/virtue_log/record")
async def create_virtue_log(request: VirtueLogCreateRequest):
    """Create a new virtue log entry and return queued mock status."""
    return {
        "status": "queued",
        "entry": {
            "id": "log_new_001",
            "user_id": request.user_id,
            "action": request.action,
            "virtues": {
                "sophia": request.sophia,
                "andreia": request.andreia,
                "dikaiosyne": request.dikaiosyne,
                "sophrosyne": request.sophrosyne,
            },
            "total_score": (
                request.sophia
                + request.andreia
                + request.dikaiosyne
                + request.sophrosyne
            ),
        },
    }
