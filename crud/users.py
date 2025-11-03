from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from models import User
from utils.events import log_event
import random


# -----------------------------
# Create User
# -----------------------------
async def create_user(
    db: AsyncSession,
    username: str,
    password: str,
    frozen_days: int = 0,
    xp: int = 0
):
    # check if username already exists
    result = await db.execute(select(User).where(User.username == username))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=username, password=password,
                frozen_days=frozen_days, xp=xp)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # log event
    await log_event(
        db,
        event_type="user_created",
        user_id=user.id,
        payload={
            "username": user.username,
            "xp": user.xp,
            "frozen_days": user.frozen_days
        }
    )
    return user


# -----------------------------
# Get User by Username
# -----------------------------
async def get_user(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -----------------------------
# Get All Users (Ranked by XP)
# -----------------------------
async def get_all_users_ranked(db: AsyncSession):
    result = await db.execute(select(User).order_by(User.xp.desc()))
    return result.scalars().all()


# -----------------------------
# Seed Users
# -----------------------------
async def seed_users(db: AsyncSession, count: int):
    users = []
    for i in range(1, count + 1):
        user = User(
            username=f"user{i}",
            password=f"pass{i}",
            xp=random.randint(0, 100) * 10
        )
        db.add(user)
        users.append(user)

    await db.commit()
    return users
