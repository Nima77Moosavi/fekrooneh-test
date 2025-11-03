import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from models import EventLog


async def log_event(
    db: AsyncSession,
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
    await db.commit()
    await db.refresh(event)
    return event
