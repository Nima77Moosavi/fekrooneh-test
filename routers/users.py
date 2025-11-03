from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.users import create_user, get_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=dict)
async def create_user_endpoint(
    username: str,
    password: str,
    frozen_days: int = 0,
    xp: int = 0,
    db: AsyncSession = Depends(get_db)
):
    user = await create_user(db, username, password, frozen_days, xp)
    return {
        "user_id": user.id,
        "username": user.username,
        "xp": user.xp,
        "streak": user.streak,
        "max_streak": user.max_streak,
        "frozen_days": user.frozen_days,
        "last_checkin": user.last_checkin,
        "last_streak_reset": user.last_streak_reset,
        "rank": user.rank,
    }


@router.get("/{username}", response_model=dict)
async def read_one_user(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, username)
    return {
        "user_id": user.id,
        "username": user.username,
        "xp": user.xp,
        "streak": user.streak,
        "max_streak": user.max_streak,
        "rank": user.rank,
        "frozen_days": user.frozen_days,
        "last_checkin": user.last_checkin,
        "last_streak_reset": user.last_streak_reset,
        "rank": user.rank,
    }
