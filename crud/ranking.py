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


async def get_leaderboard_page(page: int = 1, page_size: int = 50):
    """
    Fetch the target page with custom page size from leaderboard from Redis with ranks.
    """
    total = await redis_client.zcard("leaderboard:global")
    start = (page - 1) * page_size
    end = start + page_size - 1

    leaderboard = await redis_client.zrevrange(
        "leaderboard:global", start, end, withscores=True
    )
    users = [
        {"rank": start + i + 1, "user": user, "xp": int(xp)}
        for i, (user, xp) in enumerate(leaderboard)
    ]

    return {
        "page": page,
        "page_size": page_size,
        "total_users": total,
        "total_pages": (total + page_size - 1) // page_size,
        "users": users
    }


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


async def get_users_rank_with_range(start: int, end: int):
    """
    Fetch the top N users from Redis.
    """
    leaderboard = await redis_client.zrevrange(
        "leaderboard:global", start - 1, end - 1, withscores=True
    )
    return [
        {"rank": start + i, "user": user, "xp": int(xp)}
        for i, (user, xp) in enumerate(leaderboard)
    ]
