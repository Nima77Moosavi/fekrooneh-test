from fastapi import FastAPI
from routers import checkin, leaderboard, seed, users

app = FastAPI()

app.include_router(checkin.router)
app.include_router(leaderboard.router)
app.include_router(seed.router)
app.include_router(users.router)
