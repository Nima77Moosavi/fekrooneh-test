from pydantic import BaseModel, ConfigDict
from datetime import date


class UserResponse(BaseModel):
    id: int
    username: str
    xp: int
    streak: int
    frozen_days: int
    last_checkin: date | None
    rank: int | None
    league_id: int | None

    model_config = ConfigDict(from_attributes=True)
