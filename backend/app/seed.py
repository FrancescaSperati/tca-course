from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Habit

SEED_HABITS = [("eat", "🍽️"), ("drink", "💧"), ("read", "📚")]


def seed(db: Session) -> None:
    if db.scalar(select(Habit.id).limit(1)) is None:
        db.add_all(Habit(name=n, emoji=e) for n, e in SEED_HABITS)
        db.commit()
