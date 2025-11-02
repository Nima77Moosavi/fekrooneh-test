import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from models import EventLog


def log_event(
    db: Session,
    event_type: str,
    user_id: int,
    payload: dict,
    partition_key: str = None,
    correlation_id: str = None,
    request_id: str = None,
    source: str = "api",
    version: str = "v1"
):
    event = EventLog(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        user_id=user_id,
        partition_key=partition_key or str(user_id),
        payload=payload,
        created_at=datetime.utcnow(),
        processed=False,
        correlation_id=correlation_id,
        request_id=request_id,
    )
    db.add(event)
    # ⚠️ Don’t commit here — let the caller decide when to commit
    return event
