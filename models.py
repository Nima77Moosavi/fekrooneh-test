from sqlalchemy import Column, Integer, Boolean, String, Date, DateTime, JSON
from database import Base

from datetime import datetime
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    xp = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    frozen_days = Column(Integer, default=0)
    last_checkin = Column(Date, nullable=True)
    last_streak_reset = Column(Date, nullable=True)
    rank = Column(Integer, index=True, nullable=True)

    def __repr__(self):
        return (
            f"<User(username={self.username}, xp={self.xp}, "
            f"streak={self.streak}, rank={self.rank})>"
        )


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Unique event identity
    event_id = Column(String, unique=True, index=True,
                      default=lambda: str(uuid.uuid4()))

    # Classification
    event_type = Column(String, index=True)  # e.g. "checkin", "user_created"
    user_id = Column(Integer, index=True)
    # e.g. user_id or league_id for ordering
    partition_key = Column(String, index=True)

    # Payload (flexible JSON)
    payload = Column(JSON)

    # Lifecycle
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)    # has a consumer handled it?
    processed_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    error = Column(String, nullable=True)

    # Tracing
    correlation_id = Column(
        String, index=True, nullable=True)  # tie related events
    # link to API request
    request_id = Column(String, index=True, nullable=True)
