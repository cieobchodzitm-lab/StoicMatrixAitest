"""Health check router."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/api/health")
async def health_check():
    """Return service health status."""
    return {
        "status": "ok",
        "services": {
            "ollama": "mock",
            "postgres": "mock",
            "solana": "mock",
        },
    }
