from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.ranking import get_full_leaderboard, get_top_n, sync_ranks_to_db

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/all")
async def get_leaderboard_all():
    """
    Return the full leaderboard from Redis with ranks and XP.
    """
    leaderboard = await get_full_leaderboard()
    if not leaderboard:
        raise HTTPException(status_code=404, detail="Leaderboard is empty")
    return leaderboard


@router.get("/top/{n}")
async def get_leaderboard_top(n: int = 10):
    """
    Return the top N users from Redis leaderboard.
    """
    leaderboard = await get_top_n(n)
    if not leaderboard:
        raise HTTPException(status_code=404, detail="Leaderboard is empty")
    return leaderboard

@router.post("/sync-leaderboard")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    await sync_ranks_to_db(db)
    return {"status": "ok", "message": "Leaderboard synced to DB"}
