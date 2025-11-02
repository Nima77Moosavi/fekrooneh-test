from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import EventLog

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=list[dict])
def get_events(db: Session = Depends(get_db)):
    events = db.query(EventLog).order_by(EventLog.created_at.desc()).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "user_id": e.user_id,
            "payload": e.payload,
            "created_at": e.created_at
        }
        for e in events
    ]
