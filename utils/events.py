from sqlalchemy.orm import Session
from models import EventLog


def log_event(db: Session, event_type: str, user_id: int, payload: dict):
    event = EventLog(event_type=event_type, user_id=user_id, payload=payload)
    db.add(event)
    db.commit()

