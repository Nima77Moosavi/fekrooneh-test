# main.py
from sqlalchemy import func
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from database import SessionLocal
import models

app = FastAPI()


# Dependency: provide a database session for each request
def get_db():
    """
    Open a new database session for the request and close it afterwards.
    This ensures we don't leak connections.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=dict)
def create_user(username: str, db: Session = Depends(get_db)):
    """
    Create a new user with default XP, streak, and frozen days.
    """
    user = models.User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}


@app.post("/checkin/{user_id}", response_model=dict)
def daily_checkin(user_id: int, db: Session = Depends(get_db)):
    """
    Daily login endpoint:
    - +10 XP on check-in
    - Update streak (consecutive days)
    - Consume frozen day if user missed exactly one day
    - Reset streak if user missed 2+ days
    """
    # Use Session.get() instead of Query.get() to avoid deprecation warnings
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today = date.today()

    # Already checked in today
    if user.last_checkin == today:
        return {"message": "Already checked in today", "xp": user.xp, "streak": user.streak}

    if user.last_checkin:
        delta = (today - user.last_checkin).days
        if delta == 1:
            # consecutive day
            user.streak += 1
        elif delta == 2 and user.frozen_days > 0:
            # missed one day, consume frozen day
            user.frozen_days -= 1
            user.streak += 1
        else:
            # missed 2+ consecutive days
            user.streak = 1
    else:
        # first ever check-in
        user.streak = 1

    user.xp += 10
    user.last_checkin = today

    db.commit()
    db.refresh(user)

    return {"xp": user.xp, "streak": user.streak, "frozen_days": user.frozen_days}


@app.get("/leagues/{league_id}", response_model=list[dict])
def get_league(league_id: int, db: Session = Depends(get_db)):
    """
    Return all users in a given league (50 users per league).

    Current approach:
    - Uses SQL OFFSET + LIMIT to fetch only the 50 users for the requested league.
    - Efficient with proper indexing on `xp`, even with millions of users.

    Production optimization:
    - Precompute `league_id` for each user in a background job (cron or Celery).
    - Then this endpoint becomes a simple O(1) query:
        SELECT * FROM users WHERE league_id = :league_id
    """
    page_size = 50
    offset = (league_id - 1) * page_size

    league_users = (
        db.query(models.User)
        .order_by(models.User.xp.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return [
        {"id": u.id, "username": u.username, "xp": u.xp, "streak": u.streak}
        for u in league_users
    ]


@app.get("/users/{user_id}/league", response_model=dict)
def get_user_league(user_id: int, db: Session = Depends(get_db)):
    """
    Find which league a specific user belongs to.

    Current approach:
    - Uses a SQL window function (ROW_NUMBER() OVER ORDER BY xp DESC).
    - Guarantees every user has a unique sequential rank, even if XP values are tied.
    - This ensures exactly 50 users per league.

    Alternative approach:
    - Use RANK() if you want ties to share the same rank (like in sports),
      but then leagues may overflow/underflow.
    - For predictable league sizes, ROW_NUMBER() is the better choice.

    Production optimization:
    - Run a periodic batch job (cron or Celery) that updates `rank` and `league_id`.
    - Then this endpoint is just:
        SELECT rank, league_id FROM users WHERE id = :user_id
    - O(1) lookup, no heavy ranking query.
    """
    subq = (
        db.query(
            models.User.id,
            func.row_number().over(order_by=models.User.xp.desc()).label("rank")
        ).subquery()
    )

    row = db.query(subq.c.rank).filter(subq.c.id == user_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    rank = row.rank
    league_id = (rank - 1) // 50 + 1

    return {"user_id": user_id, "league_id": league_id, "rank": rank}
