import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User

# Redis client
redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)


# -----------------------------
# Update Leaderboard in Redis
# -----------------------------
async def update_leaderboard(user_id: int, xp: int):
    """
    Add or update a user's XP in the Redis leaderboard.
    """
    await redis_client.zadd("leaderboard:global", {f"user:{user_id}": xp})


# -----------------------------
# Get Full Leaderboard
# -----------------------------
async def get_full_leaderboard():
    """
    Fetch the entire leaderboard from Redis with ranks.
    """
    leaderboard = await redis_client.zrevrange(
        "leaderboard:global", 0, -1, withscores=True
    )
    return [
        {"rank": i + 1, "user": user, "xp": int(xp)}
        for i, (user, xp) in enumerate(leaderboard)
    ]


# -----------------------------
# Get Top N Users
# -----------------------------
async def get_top_n(n: int = 10):
    """
    Fetch the top N users from Redis.
    """
    leaderboard = await redis_client.zrevrange(
        "leaderboard:global", 0, n - 1, withscores=True
    )
    return [
        {"rank": i + 1, "user": user, "xp": int(xp)}
        for i, (user, xp) in enumerate(leaderboard)
    ]


# -----------------------------
# Sync Back to Database
# -----------------------------
async def sync_ranks_to_db(db: AsyncSession):
    """
    Periodically sync Redis leaderboard ranks back into the SQL database.
    """
    leaderboard = await redis_client.zrevrange(
        "leaderboard:global", 0, -1, withscores=True
    )

    for rank, (user_key, xp) in enumerate(leaderboard, start=1):
        user_id = int(user_key.split(":")[1])
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.rank = rank
            user.xp = int(xp)
            db.add(user)

    await db.commit()
