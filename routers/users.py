from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=dict)
def create_user(username: str, password: str, frozen_days: int = 0, xp: int = 0, db: Session = Depends(get_db)):
    user = crud.create_user(db, username, password, frozen_days, xp)
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
        "league_id": user.league_id
    }

@router.get("/{username}", response_model=dict)
def read_one_user(username: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, username)
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
        "league_id": user.league_id
    }

@router.get("/{username}/league", response_model=dict)
def get_user_league(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_league(db, username)
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
        "league_id": user.league_id
    }
