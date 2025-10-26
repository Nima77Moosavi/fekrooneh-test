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
