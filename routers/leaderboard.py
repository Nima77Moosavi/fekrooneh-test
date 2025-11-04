from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.ranking import get_leaderboard_page, get_top_n, get_users_rank_with_range

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/all")
async def get_leaderboard_all(page: int = 1, page_size: int = 50):
    """
    Return a paginated leaderboard from Redis.
    """
    data = await get_leaderboard_page(page, page_size)
    return data


@router.get("/top/{n}")
async def get_leaderboard_top(n: int = 10):
    """
    Return the top N users from Redis leaderboard.
    """
    leaderboard = await get_top_n(n)
    if not leaderboard:
        raise HTTPException(status_code=404, detail="Leaderboard is empty")
    return leaderboard


@router.get("/range/{start}/{end}")
async def get_leaderboard_range(start: int, end: int):
    """
    Return a range of users in leaderboard from start to end ranks.
    """
    leaderboard = await get_users_rank_with_range(start, end)
    if not leaderboard:
        raise HTTPException(
            status_code=404, detail="leaderboard range is empty"
        )
    return leaderboard
