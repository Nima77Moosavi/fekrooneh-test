# events/consumer.py
import asyncio, json
import redis.asyncio as redis

async def consume_events():
    client = redis.from_url("redis://localhost:6379", decode_responses=True)
    stream = "user-events"
    group = "leaderboard-consumers"

    # Create consumer group if not exists
    try:
        await client.xgroup_create(stream, group, id="$", mkstream=True)
    except Exception:
        pass  # group already exists

    while True:
        resp = await client.xreadgroup(
            group, "consumer-1", {stream: ">"}, count=10, block=5000
        )
        if not resp:
            continue

        for _, messages in resp:
            for msg_id, fields in messages:
                event = json.loads(fields["data"])
                print("Processing event:", event)

                if event["event_type"] == "checkin":
                    # Update leaderboard (sorted set)
                    await client.zincrby(
                        "leaderboard:global",
                        event["xp_increment"],
                        f"user:{event['user_id']}"
                    )

                # Acknowledge event
                await client.xack(stream, group, msg_id)

if __name__ == "__main__":
    asyncio.run(consume_events())
