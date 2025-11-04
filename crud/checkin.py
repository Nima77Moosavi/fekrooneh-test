from datetime import date
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User
from utils.events import log_event


# -----------------------------
# Daily Check-in
# -----------------------------
async def daily_checkin(db: AsyncSession, username: str, password: str):
    # Fetch user
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.password != password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    today = date.today()

    # if already checked in today return a message with xp
    if user.last_checkin == today:
        return user, False

    # Only update if not already checked in today
    if user.last_checkin != today:
        if user.last_checkin:
            delta = (today - user.last_checkin).days
            if delta == 1:
                # consecutive day
                user.streak += 1
            elif delta >= 2 and user.frozen_days >= (delta - 1):
                # missed days but can consume frozen days
                user.streak += 1
                user.frozen_days -= (delta - 1)
            else:
                # streak broken
                user.streak = 1
                user.frozen_days = 1
                user.last_streak_reset = today
        else:
            # first ever check-in
            user.streak = 1
            if user.frozen_days == 0:
                user.frozen_days = 1

        # update max streak
        if user.streak > user.max_streak:
            user.max_streak = user.streak

        # reward XP
        user.xp += 10
        user.last_checkin = today

        await db.commit()
        await db.refresh(user)

        # log event
        await log_event(
            db,
            event_type="checkin",
            user_id=user.id,
            payload={
                "xp_gained": 10,
                "new_total": user.xp,
                "streak": user.streak,
                "frozen_days": user.frozen_days,
            },
        )

    return user, True
