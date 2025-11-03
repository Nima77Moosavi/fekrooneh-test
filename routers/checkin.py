from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.checkin import daily_checkin
from events.producer import publish_event

router = APIRouter(prefix="/checkin", tags=["checkin"])


@router.post("/")
async def daily_checkin_endpoint(
    username: str,
    password: str,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    # call async CRUD
    user = await daily_checkin(db, username, password)

    # prepare event payload for Redis
    event_payload = {
        "event_type": "checkin",
        "user_id": user.id,
        "xp": user.xp,
        "xp_increment": 10,
        "streak": user.streak,
        "max_streak": user.max_streak,
        "frozen_days": user.frozen_days,
        "last_checkin": str(user.last_checkin),
        "last_streak_reset": str(user.last_streak_reset),
    }

    # publish asynchronously in background
    if background_tasks:
        background_tasks.add_task(publish_event, event_payload)

    return {
        "message": "Check-in successful",
        "xp": user.xp,
        "streak": user.streak,
        "max_streak": user.max_streak,
        "frozen_days": user.frozen_days,
        "last_streak_reset": user.last_streak_reset,
    }
