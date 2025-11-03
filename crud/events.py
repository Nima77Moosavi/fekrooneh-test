import redis.asyncio as redis
import uuid
import json
from datetime import datetime

redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

async def publish_event(event_type: str, user_id: int, payload: dict):
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "user_id": user_id,
        "payload": json.dumps(payload),
        "created_at": datetime.utcnow().isoformat(),
    }
    await redis_client.xadd("user-events", event)
    return event
