from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter(prefix="/checkin", tags=["checkin"])

@router.post("/", response_model=dict)
def daily_checkin(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.daily_checkin(db, username, password)
    return {
        "message": "Check-in successful",
        "xp": user.xp,
        "streak": user.streak,
        "max_streak": user.max_streak,
        "frozen_days": user.frozen_days,
        "last_streak_reset": user.last_streak_reset,
    }
