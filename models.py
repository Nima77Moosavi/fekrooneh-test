from sqlalchemy import Column, Integer, String, Date
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    xp = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    frozen_days = Column(Integer, default=1)
    last_checkin = Column(Date, nullable=True)

    def __repr__(self):
        return f"<User(username={self.username}, xp={self.xp}, streak={self.streak})>"
