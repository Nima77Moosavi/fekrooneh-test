from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter(prefix="/seed", tags=["seed"])

@router.post("/users/{count}", response_model=dict)
def seed_users(count: int, db: Session = Depends(get_db)):
    users = crud.seed_users(db, count)
    return {"message": f"{count} test users created", "count": len(users)}
