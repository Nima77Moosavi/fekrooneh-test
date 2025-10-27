from database import SessionLocal
import models

def recompute_ranks():
    """
    Recompute user ranks and league assignments.

    This function queries all users ordered by XP (highest first),
    then assigns:
      - rank: the user's global position (1 = top XP)
      - league_id: which league the user belongs to (50 users per league)

    The results are written back to the database so that endpoints
    can return rank/league instantly (O(1) lookup) instead of
    recalculating on every request.

    ⚠️ Note: This is designed to be run as a periodic batch job.
    In production, you would schedule it with a task runner such as
    Celery + Redis/RabbitMQ, or a cron job, so that ranks are
    refreshed regularly (e.g. every few minutes) without blocking
    API requests.
    """
    db = SessionLocal()
    try:
        users = db.query(models.User).order_by(models.User.xp.desc()).all()
        for idx, user in enumerate(users):
            user.rank = idx + 1
            user.league_id = (idx // 50) + 1
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    recompute_ranks()
