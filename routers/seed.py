from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.users import seed_users   # make sure seed_users lives in crud/users.py

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("/users/{count}", response_model=dict)
async def seed_users_endpoint(count: int, db: AsyncSession = Depends(get_db)):
    users = await seed_users(db, count)
    return {
        "message": f"{count} test users created",
        "count": len(users)
    }
