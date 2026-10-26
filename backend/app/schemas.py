from datetime import datetime

from pydantic import BaseModel, Field


class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    emoji: str = Field(min_length=1, max_length=16)


class HabitOut(BaseModel):
    id: int
    name: str
    emoji: str
    created_at: datetime
    completed_today: bool
    streak: int
    longest_streak: int
    last_completed: str | None  # YYYY-MM-DD
