# from datetime import date
# import random

# from sqlalchemy import func
# from sqlalchemy.orm import Session
# from fastapi import FastAPI, Depends, HTTPException, status

# from database import SessionLocal
# import models
# from models import User, League
# from schemas import UserResponse


# from database import engine
# from models import Base

# # Create all tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI()


# # Dependency: provide a database session for each request
# def get_db():
#     """
#     Open a new database session for the request and close it afterwards.
#     This ensures we don't leak connections.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # assign users global ranking
# def assign_global_ranks(db: Session):
#     subq = (
#         db.query(
#             User.id,
#             func.row_number().over(order_by=User.xp.desc()).label("rank")
#         ).subquery()
#     )

#     ranked_users = db.query(User, subq.c.rank).join(
#         subq, User.id == subq.c.id).all()

#     for user, rank in ranked_users:
#         user.rank = rank

#     db.commit()


# # assign users leagues
# def assign_leagues(db: Session):
#     subq = (
#         db.query(
#             User.id,
#             func.row_number().over(order_by=User.xp.desc()).label("rank")
#         ).subquery()
#     )

#     ranked_users = db.query(User, subq.c.rank).join(
#         subq, User.id == subq.c.id).all()

#     for user, rank in ranked_users:
#         league_id = (rank - 1) // 50 + 1

#         league = db.query(League).filter(League.id == league_id).first()
#         if not league:
#             league = League(id=league_id)
#             db.add(league)
#             db.commit()

#         user.rank = rank
#         user.league_id = league_id

#     db.commit()


# @app.post("/seed_users/{count}", response_model=dict)
# def seed_users(count: int, db: Session = Depends(get_db)):
#     users = []
#     for i in range(1, count + 1):
#         user = User(
#             username=f"user{i}",
#             password=f"pass{i}",
#             xp=random.randint(0, 100) * 10
#         )
#         db.add(user)
#         users.append(user)

#     db.commit()
#     assign_leagues(db)

#     return {"message": f"{count} test users created", "count": len(users)}


# @app.post("/users/", response_model=dict)
# def create_user(username: str, password: str, frozen_days: int = 0, xp: int = 0, db: Session = Depends(get_db)):
#     existing = db.query(User).filter(User.username == username).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Username already exists")

#     user = User(username=username, password=password, frozen_days=frozen_days, xp=xp)
#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     assign_leagues(db)
#     assign_global_ranks(db)
#     return {
#         "user_id": user.id,
#         "username": user.username,
#         "xp": user.xp,
#         "streak": user.streak,
#         "max_streak": user.max_streak,
#         "frozen_days": user.frozen_days,
#         "last_checkin": user.last_checkin,
#         "last_streak_reset": user.last_streak_reset,
#         "rank": user.rank,
#         "league_id": user.league_id
#     }


# @app.get("/users/{username}")
# def read_one_user(username: str, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == username).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {
#         "user_id": user.id,
#         "username": user.username,
#         "xp": user.xp,
#         "streak": user.streak,
#         "max_streak": user.max_streak,
#         "frozen_days": user.frozen_days,
#         "last_checkin": user.last_checkin,
#         "last_streak_reset": user.last_streak_reset,
#         "rank": user.rank,
#         "league_id": user.league_id
#     }


# @app.post("/checkin/", response_model=dict)
# def daily_checkin(username: str, password: str, db: Session = Depends(get_db)):
#     """
#     Daily login endpoint:
#     - +10 XP on check-in
#     - Update streak (consecutive days)
#     - Consume frozen day if user missed exactly one day
#     - Reset streak if user missed 2+ days
#     - Track max_streak and last_streak_reset
#     """
#     user = db.query(User).filter(User.username == username).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if user.password != password:
#         raise HTTPException(status_code=401, detail="Incorrect password")

#     today = date.today()

#     # Already checked in today
#     if user.last_checkin == today:
#         return {
#             "message": "Already checked in today",
#             "xp": user.xp,
#             "streak": user.streak,
#             "max_streak": user.max_streak,
#             "frozen_days": user.frozen_days,
#         }

#     if user.last_checkin:
#         delta = (today - user.last_checkin).days
#         if delta == 1:
#             # consecutive day
#             user.streak += 1
#         elif delta >= 2 and user.frozen_days >= (delta - 1):
#             # missed one day, consume frozen day
#             user.streak += 1
#             user.frozen_days -= (delta - 1)
#             # streak unchanged
#         else:
#             # missed 1 day without freeze OR missed 2+ days
#             user.streak = 1
#             user.frozen_days = 1
#             user.last_streak_reset = today
#     else:
#         # first ever check-in
#         user.streak = 1
#         if user.frozen_days == 0:
#             user.frozen_days = 1

#     # update max streak if needed
#     if user.streak > user.max_streak:
#         user.max_streak = user.streak

#     user.xp += 10
#     user.last_checkin = today

#     db.commit()
#     db.refresh(user)
#     assign_leagues(db)
#     assign_global_ranks(db)

#     return {
#         "message": "Check-in successful",
#         "xp": user.xp,
#         "streak": user.streak,
#         "max_streak": user.max_streak,
#         "frozen_days": user.frozen_days,
#         "last_streak_reset": user.last_streak_reset,
#     }


# @app.get("/leagues/{league_id}", response_model=list[dict])
# def get_league_by_id(league_id: int, db: Session = Depends(get_db)):
#     """
#     Return all users in a given league (50 users per league).
#     Uses precomputed league_id and rank from assign_leagues.
#     """
#     league_users = (
#         db.query(User)
#         .filter(User.league_id == league_id)
#         .order_by(User.rank.asc())
#         .all()
#     )

#     if not league_users:
#         raise HTTPException(
#             status_code=404, detail="League not found or empty")

#     return [
#         {
#             "user_id": user.id,
#             "username": user.username,
#             "xp": user.xp,
#             "streak": user.streak,
#             "max_streak": user.max_streak,
#             "frozen_days": user.frozen_days,
#             "last_checkin": user.last_checkin,
#             "last_streak_reset": user.last_streak_reset,
#             "rank": user.rank,
#             "league_id": user.league_id
#         }
#         for user in league_users
#     ]


# @app.get("/league/", response_model=list[dict])
# def get_league(db: Session = Depends(get_db)):
#     users = (
#         db.query(User)
#         .order_by(User.rank.asc())
#         .all()
#     )

#     return [
#         {
#             "user_id": user.id,
#             "username": user.username,
#             "xp": user.xp,
#             "streak": user.streak,
#             "max_streak": user.max_streak,
#             "frozen_days": user.frozen_days,
#             "last_checkin": user.last_checkin,
#             "last_streak_reset": user.last_streak_reset,
#             "rank": user.rank,
#             "league_id": user.league_id
#         }
#         for user in users
#     ]


# @app.get("/users/{username}/league", response_model=dict)
# def get_user_league(username: str, db: Session = Depends(get_db)):
#     """
#     Return the league and rank of a specific user.
#     Uses precomputed rank and league_id from assign_leagues.
#     """
#     user = db.query(User).filter(User.username == username).first()

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     return {
#         "user_id": user.id,
#         "username": user.username,
#         "xp": user.xp,
#         "streak": user.streak,
#         "max_streak": user.max_streak,
#         "frozen_days": user.frozen_days,
#         "last_checkin": user.last_checkin,
#         "last_streak_reset": user.last_streak_reset,
#         "rank": user.rank,
#         "league_id": user.league_id
#     }


from fastapi import FastAPI
from routers import users, checkin, leagues, seed
from consumers.rank_consumer import process_checkin_events
import asyncio

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_checkin_events())

app.include_router(users.router)
app.include_router(checkin.router)
app.include_router(leagues.router)
app.include_router(seed.router)
