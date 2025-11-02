import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models import EventLog, User
from crud import assign_global_ranks, assign_leagues


async def process_checkin_events():
    while True:
        db: Session = SessionLocal()
        try:
            # fetch unprocessed checkin events
            events = db.query(EventLog).filter_by(
                processed=False, event_type="checkin"
            ).all()

            for event in events:
                # update rank for this user
                update_rank(db, event.user_id)

                # also run your league/global rank logic
                assign_leagues(db)
                assign_global_ranks(db)

                # mark event as processed
                event.processed = True
                event.processed_at = datetime.utcnow()

            db.commit()
        finally:
            db.close()

        await asyncio.sleep(5)


def update_rank(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    higher_xp_users_count = db.query(User).filter(User.xp > user.xp).count()
    user.rank = higher_xp_users_count + 1
    # don’t commit here — let the caller commit
