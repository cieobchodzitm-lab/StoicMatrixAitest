# backend/routers/cnota_optimized.py
# 🚀 Optimized CNOTA Router with Connection Pooling, Caching & Async

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import List, Optional
import logging
from datetime import datetime, timedelta
import asyncio

from backend.cache import cached, invalidate_cache
from backend.models import User, Virtue, Score

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cnota", tags=["cnota"])

# ========================
# OPTIMIZED ENDPOINTS
# ========================

@router.get("/profile/{user_id}")
@cached(ttl=300, key_prefix="cnota:profile")
async def get_user_profile(user_id: int, db: AsyncSession = Depends()):
    """
    Get user virtue profile with caching
    
    ✅ Optimizations:
    - Eager loading with joinedload
    - Redis caching (5 min TTL)
    - Async database queries
    """
    try:
        # Single query with eager loading
        stmt = select(User).options(
            joinedload(User.virtues),
            joinedload(User.nft_passport),
            joinedload(User.scores)
        ).where(User.id == user_id)
        
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return {"error": "User not found"}, 404
        
        return {
            "id": user.id,
            "username": user.username,
            "virtues": [
                {
                    "type": v.virtue_type,
                    "score": v.score,
                    "updated_at": v.updated_at
                }
                for v in user.virtues
            ],
            "nft_passport": user.nft_passport.to_dict() if user.nft_passport else None,
            "total_score": sum(v.score for v in user.virtues)
        }
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise

@router.get("/leaderboard")
@cached(ttl=600, key_prefix="cnota:leaderboard")  # 10 min cache
async def get_leaderboard(
    virtue_type: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends()
):
    """
    Get paginated leaderboard with caching
    
    ✅ Optimizations:
    - Parallel queries with asyncio.gather
    - Database pagination
    - Result caching
    """
    try:
        # Build base query
        base_query = select(User).options(
            joinedload(User.virtues)
        )
        
        # Filter by virtue if specified
        if virtue_type:
            base_query = base_query.where(
                User.virtues.any(Virtue.virtue_type == virtue_type)
            )
        
        # Get total count and paginated results in parallel
        count_stmt = select(func.count(User.id))
        results_stmt = base_query.offset(offset).limit(limit)
        
        count_result, results = await asyncio.gather(
            db.execute(count_stmt),
            db.execute(results_stmt)
        )
        
        total = count_result.scalar()
        users = results.scalars().all()
        
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "leaderboard": [
                {
                    "rank": offset + i + 1,
                    "user_id": u.id,
                    "username": u.username,
                    "scores": {
                        v.virtue_type: v.score
                        for v in u.virtues
                    },
                    "total_score": sum(v.score for v in u.virtues)
                }
                for i, u in enumerate(users)
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        raise

@router.post("/score")
async def calculate_score(
    user_id: int,
    virtue_type: str,
    value: float,
    db: AsyncSession = Depends()
):
    """
    Calculate and store virtue score
    
    ✅ Optimizations:
    - Atomic transaction
    - Cache invalidation
    - Async operations
    """
    try:
        # Get or create score record
        stmt = select(Score).where(
            (Score.user_id == user_id) &
            (Score.virtue_type == virtue_type)
        )
        
        result = await db.execute(stmt)
        score = result.scalar_one_or_none()
        
        if score:
            score.value = value
            score.updated_at = datetime.utcnow()
        else:
            score = Score(
                user_id=user_id,
                virtue_type=virtue_type,
                value=value
            )
            db.add(score)
        
        await db.commit()
        
        # Invalidate relevant caches
        invalidate_cache(f"cnota:profile:{user_id}")
        invalidate_cache("cnota:leaderboard*")
        
        logger.info(f"✅ Score calculated: user={user_id}, virtue={virtue_type}")
        
        return {
            "user_id": user_id,
            "virtue_type": virtue_type,
            "value": value,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error calculating score: {e}")
        raise

@router.get("/stats")
@cached(ttl=900, key_prefix="cnota:stats")  # 15 min cache
async def get_statistics(db: AsyncSession = Depends()):
    """
    Get platform statistics
    
    ✅ Optimizations:
    - Multiple aggregation queries in parallel
    - Result caching
    """
    try:
        # Execute multiple aggregation queries in parallel
        results = await asyncio.gather(
            db.execute(select(func.count(User.id))),
            db.execute(select(func.avg(Score.value))),
            db.execute(select(func.max(Score.value))),
            db.execute(select(func.min(Score.value)))
        )
        
        total_users = results[0].scalar() or 0
        avg_score = results[1].scalar() or 0
        max_score = results[2].scalar() or 0
        min_score = results[3].scalar() or 0
        
        return {
            "total_users": total_users,
            "average_score": float(avg_score),
            "max_score": float(max_score),
            "min_score": float(min_score),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise
