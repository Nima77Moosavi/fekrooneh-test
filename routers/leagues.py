from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter(prefix="/leagues", tags=["leagues"])


@router.get("/{league_id}", response_model=list[dict])
def get_league_by_id(league_id: int, db: Session = Depends(get_db)):
    league_users = crud.get_league_by_id(db, league_id)
    return [
        {
            "user_id": u.id,
            "username": u.username,
            "xp": u.xp,
            "streak": u.streak,
            "max_streak": u.max_streak,
            "frozen_days": u.frozen_days,
            "last_checkin": u.last_checkin,
            "last_streak_reset": u.last_streak_reset,
            "rank": u.rank,
            "league_id": u.league_id
        }
        for u in league_users
    ]


@router.get("/", response_model=list[dict])
def get_all_leagues(db: Session = Depends(get_db)):
    users = crud.get_all_users_ranked(db)
    return [
        {
            "user_id": u.id,
            "username": u.username,
            "xp": u.xp,
            "streak": u.streak,
            "max_streak": u.max_streak,
            "frozen_days": u.frozen_days,
            "last_checkin": u.last_checkin,
            "last_streak_reset": u.last_streak_reset,
            "rank": u.rank,
            "league_id": u.league_id
        }
        for u in users
    ]
