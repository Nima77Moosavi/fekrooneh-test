import json
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)


async def publish_event(event_payload: dict):
    """Publish an event into Redis Stream."""
    await redis_client.xadd("user-events", fields={"data": json.dumps(event_payload)})
