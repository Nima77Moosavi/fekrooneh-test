import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User

# Redis client
redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
LEADERBOARD_KEY = "leaderboard:global"

async def add_user_to_leaderboard(user_id: int, xp: int = 0):
    await redis_client.zadd(LEADERBOARD_KEY, {f"user:{user_id}": xp})
    
async def sync_all_users_to_redis(db: AsyncSession):
    result = await db.execute(select(User.id, User.xp))
    for user_id, xp in result.all():
        await redis_client.zadd(LEADERBOARD_KEY, {f"user:{user_id}": xp})

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
        LEADERBOARD_KEY, 0, -1, withscores=True
    )

    # Fetch all users in one query
    user_ids = [int(user_key.split(":")[1]) for user_key, _ in leaderboard]
    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = {u.id: u for u in result.scalars().all()}

    # Update ranks and XP
    for rank, (user_key, xp) in enumerate(leaderboard, start=1):
        user_id = int(user_key.split(":")[1])
        user = users.get(user_id)
        if user:
            user.rank = rank
            user.xp = int(xp)

    await db.commit()

