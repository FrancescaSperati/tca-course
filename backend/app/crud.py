from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Completion, Habit
from .schemas import HabitOut


def today() -> date:
    return date.today()


def compute_streak(dates: set[str], current: date) -> int:
    """Consecutive completed days counting back from today.

    An unticked today doesn't break the streak: counting then starts yesterday.
    """
    day = current if current.isoformat() in dates else current - timedelta(days=1)
    streak = 0
    while day.isoformat() in dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


def compute_longest_streak(dates: set[str]) -> int:
    """Longest run of consecutive completed days anywhere in the history."""
    longest = run = 0
    prev: date | None = None
    for d in sorted(date.fromisoformat(s) for s in dates):
        run = run + 1 if prev is not None and d - prev == timedelta(days=1) else 1
        longest = max(longest, run)
        prev = d
    return longest


def _to_out(habit: Habit, dates: set[str], current: date) -> HabitOut:
    return HabitOut(
        id=habit.id,
        name=habit.name,
        emoji=habit.emoji,
        created_at=habit.created_at,
        completed_today=current.isoformat() in dates,
        streak=compute_streak(dates, current),
        longest_streak=compute_longest_streak(dates),
        last_completed=max(dates) if dates else None,
    )


def list_habits(db: Session) -> list[HabitOut]:
    current = today()
    by_habit: dict[int, set[str]] = {}
    for habit_id, d in db.execute(select(Completion.habit_id, Completion.completed_date)):
        by_habit.setdefault(habit_id, set()).add(d)
    habits = db.scalars(select(Habit).order_by(Habit.id)).all()
    return [_to_out(h, by_habit.get(h.id, set()), current) for h in habits]


def get_habit(db: Session, habit_id: int) -> HabitOut | None:
    habit = db.get(Habit, habit_id)
    if habit is None:
        return None
    dates = set(db.scalars(select(Completion.completed_date).where(Completion.habit_id == habit_id)))
    return _to_out(habit, dates, today())


def create_habit(db: Session, name: str, emoji: str) -> HabitOut:
    habit = Habit(name=name.strip(), emoji=emoji.strip())
    db.add(habit)
    db.commit()
    return get_habit(db, habit.id)


def set_today(db: Session, habit_id: int, done: bool) -> HabitOut | None:
    if db.get(Habit, habit_id) is None:
        return None
    day = today().isoformat()
    existing = db.scalar(
        select(Completion).where(Completion.habit_id == habit_id, Completion.completed_date == day)
    )
    if done and existing is None:
        db.add(Completion(habit_id=habit_id, completed_date=day))
        db.commit()
    elif not done and existing is not None:
        db.delete(existing)
        db.commit()
    return get_habit(db, habit_id)
