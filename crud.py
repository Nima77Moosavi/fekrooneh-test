from datetime import date
import random

from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi import BackgroundTasks

import redis.asyncio as redis

from models import User, League
from utils.events import log_event
from events.producer import publish_event

redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)


# -----------------------------
# Ranking & League Assignment
# -----------------------------
def assign_global_ranks(db: Session):
    subq = (
        db.query(
            User.id,
            func.row_number().over(order_by=User.xp.desc()).label("rank")
        ).subquery()
    )
    ranked_users = db.query(User, subq.c.rank).join(
        subq, User.id == subq.c.id).all()
    for user, rank in ranked_users:
        user.rank = rank
    db.commit()


def assign_leagues(db: Session):
    subq = (
        db.query(
            User.id,
            func.row_number().over(order_by=User.xp.desc()).label("rank")
        ).subquery()
    )
    ranked_users = db.query(User, subq.c.rank).join(
        subq, User.id == subq.c.id).all()
    for user, rank in ranked_users:
        league_id = (rank - 1) // 50 + 1
        league = db.query(League).filter(League.id == league_id).first()
        if not league:
            league = League(id=league_id)
            db.add(league)
            db.commit()
        user.rank = rank
        user.league_id = league_id
    db.commit()


# -----------------------------
# User Operations
# -----------------------------
def create_user(db: Session, username: str, password: str, frozen_days: int = 0, xp: int = 0):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=username, password=password,
                frozen_days=frozen_days, xp=xp)
    db.add(user)
    db.commit()
    db.refresh(user)

    assign_leagues(db)
    assign_global_ranks(db)

    # log event
    log_event(
        db,
        event_type="user_created",
        user_id=user.id,
        payload={"username": user.username, "xp": user.xp,
                 "frozen_days": user.frozen_days}
    )
    return user


def get_user(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_league(db: Session, username: str):
    user = get_user(db, username)
    return user


# -----------------------------
# Check-in Logic
# -----------------------------
def daily_checkin(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.password != password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    today = date.today()

    if user.last_checkin != today:
        if user.last_checkin:
            delta = (today - user.last_checkin).days
            if delta == 1:
                user.streak += 1
            elif delta >= 2 and user.frozen_days >= (delta - 1):
                user.streak += 1
                user.frozen_days -= (delta - 1)
            else:
                user.streak = 1
                user.frozen_days = 1
                user.last_streak_reset = today
        else:
            user.streak = 1
            if user.frozen_days == 0:
                user.frozen_days = 1

        if user.streak > user.max_streak:
            user.max_streak = user.streak

        user.xp += 10
        user.last_checkin = today

        db.commit()
        db.refresh(user)

    return user


# -----------------------------
# League Queries
# -----------------------------
def get_league_by_id(db: Session, league_id: int):
    league_users = (
        db.query(User)
        .filter(User.league_id == league_id)
        .order_by(User.rank.asc())
        .all()
    )
    if not league_users:
        raise HTTPException(
            status_code=404, detail="League not found or empty")
    return league_users


def get_all_users_ranked(db: Session):
    return db.query(User).order_by(User.rank.asc()).all()


# -----------------------------
# Seeding
# -----------------------------
def seed_users(db: Session, count: int):
    users = []
    for i in range(1, count + 1):
        user = User(
            username=f"user{i}",
            password=f"pass{i}",
            xp=random.randint(0, 100) * 10
        )
        db.add(user)
        users.append(user)
    db.commit()
    assign_leagues(db)
    return users
