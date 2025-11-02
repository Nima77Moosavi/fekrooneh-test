from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import Relationship
from database import Base


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)

    def __repr__(self):
        return f"<League(id={self.id})>"


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
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=True)
    league = Relationship("League", backref='users')

    def __repr__(self):
        return f"<User(username={self.username}, xp={self.xp}, streak={self.streak}, rank={self.rank}, league={self.league_id})>"
