# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from database import SessionLocal, engine
import models

# Make sure tables exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency: get a DB session for each request


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=dict)
def create_user(username: str, db: Session = Depends(get_db)):
    """Create a new user with default XP, streak, and frozen days."""
    user = models.User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}


@app.post("/checkin/{user_id}", response_model=dict)
def daily_checkin(user_id: int, db: Session = Depends(get_db)):
    """Daily login endpoint: +10 XP, update streak, handle frozen days."""
    user = db.query(models.User).get(user_id)
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
            # missed too many days
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
    """Return all users in a given league (50 users per league)."""
    users = db.query(models.User).order_by(models.User.xp.desc()).all()
    start = (league_id - 1) * 50
    end = start + 50
    league_users = users[start:end]

    return [
        {"id": u.id, "username": u.username, "xp": u.xp, "streak": u.streak}
        for u in league_users
    ]


@app.get("/users/{user_id}/league", response_model=dict)
def get_user_league(user_id: int, db: Session = Depends(get_db)):
    """Find which league a specific user belongs to."""
    users = db.query(models.User).order_by(models.User.xp.desc()).all()
    user_ids = [u.id for u in users]

    if user_id not in user_ids:
        raise HTTPException(status_code=404, detail="User not found")

    rank = user_ids.index(user_id)  # 0-based index
    league_id = (rank // 50) + 1

    return {"user_id": user_id, "league_id": league_id, "rank": rank + 1}
