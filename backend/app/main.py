from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud
from .db import Base, SessionLocal, engine, get_db
from .schemas import HabitCreate, HabitOut
from .seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(title="Habit tracker", lifespan=lifespan)


def _or_404(habit: HabitOut | None) -> HabitOut:
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@app.get("/habits", response_model=list[HabitOut])
def list_habits(db: Session = Depends(get_db)):
    return crud.list_habits(db)


@app.post("/habits", response_model=HabitOut, status_code=201)
def create_habit(body: HabitCreate, db: Session = Depends(get_db)):
    return crud.create_habit(db, body.name, body.emoji)


@app.post("/habits/{habit_id}/complete", response_model=HabitOut)
def complete(habit_id: int, db: Session = Depends(get_db)):
    return _or_404(crud.set_today(db, habit_id, True))


@app.delete("/habits/{habit_id}/complete", response_model=HabitOut)
def uncomplete(habit_id: int, db: Session = Depends(get_db)):
    return _or_404(crud.set_today(db, habit_id, False))
