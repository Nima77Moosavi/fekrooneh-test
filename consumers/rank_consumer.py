import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal
from models import EventLog, User


async def process_checkin_events(db):
    while True:
        db: Session = SessionLocal
        try:
            events = db.query(EventLog).filter_by(
                processed=False, type="checkin").all()
            for event in events:
                update_rank(db, event.user_id)
                event.processed = True
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
    db.commit()
