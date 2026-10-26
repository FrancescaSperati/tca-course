from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import crud
from app.crud import compute_streak
from app.db import Base, get_db
from app.main import app
from app.models import Completion
from app.seed import seed

TODAY = date(2026, 10, 26)


def days_ago(n: int) -> str:
    return (TODAY - timedelta(days=n)).isoformat()


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as s:
        yield s


@pytest.fixture
def client(session, monkeypatch):
    monkeypatch.setattr(crud, "today", lambda: TODAY)
    app.dependency_overrides[get_db] = lambda: session
    yield TestClient(app)  # no lifespan: tests control seeding
    app.dependency_overrides.clear()


def add_days(session, habit_id, *offsets):
    session.add_all(Completion(habit_id=habit_id, completed_date=days_ago(n)) for n in offsets)
    session.commit()


def make_habit(client, name="walk", emoji="🚶"):
    return client.post("/habits", json={"name": name, "emoji": emoji}).json()


# --- streak maths ---

@pytest.mark.parametrize(
    "offsets, expected",
    [
        ([], 0),
        ([0], 1),
        ([0, 1, 2], 3),
        ([1, 2, 3], 3),  # today unticked doesn't break it
        ([0, 1, 3, 4], 2),  # gap ends the streak
        ([2, 3], 0),  # ended before yesterday
        ([0, 2, 3], 1),
    ],
)
def test_compute_streak(offsets, expected):
    assert compute_streak({days_ago(n) for n in offsets}, TODAY) == expected


# --- endpoints ---

def test_list_empty(client):
    assert client.get("/habits").json() == []


def test_create_and_list(client):
    r = client.post("/habits", json={"name": " run ", "emoji": "🏃"})
    assert r.status_code == 201
    body = r.json()
    assert (body["name"], body["emoji"], body["completed_today"], body["streak"]) == ("run", "🏃", False, 0)
    assert [h["id"] for h in client.get("/habits").json()] == [body["id"]]


@pytest.mark.parametrize("payload", [{}, {"name": "", "emoji": "x"}, {"name": "x", "emoji": ""}])
def test_create_validation(client, payload):
    assert client.post("/habits", json=payload).status_code == 422


def test_complete_is_idempotent(client, session):
    h = make_habit(client)
    first = client.post(f"/habits/{h['id']}/complete")
    second = client.post(f"/habits/{h['id']}/complete")
    assert first.status_code == second.status_code == 200
    assert second.json()["completed_today"] is True
    assert second.json()["streak"] == 1
    assert session.query(Completion).count() == 1


def test_uncomplete(client):
    h = make_habit(client)
    client.post(f"/habits/{h['id']}/complete")
    r = client.delete(f"/habits/{h['id']}/complete")
    assert r.json()["completed_today"] is False
    assert r.json()["streak"] == 0
    assert client.delete(f"/habits/{h['id']}/complete").status_code == 200  # already unticked


def test_streak_in_list_with_unticked_today(client, session):
    h = make_habit(client)
    add_days(session, h["id"], 1, 2, 3)
    item = client.get("/habits").json()[0]
    assert item["completed_today"] is False
    assert item["streak"] == 3
    # ticking today extends it
    assert client.post(f"/habits/{h['id']}/complete").json()["streak"] == 4


def test_unknown_habit_404(client):
    assert client.post("/habits/999/complete").status_code == 404
    assert client.delete("/habits/999/complete").status_code == 404


def test_seed_only_when_empty(session):
    seed(session)
    seed(session)
    from app.models import Habit

    assert [h.name for h in session.query(Habit).order_by(Habit.id)] == ["eat", "drink", "read"]


def test_last_completed(client, session):
    h = make_habit(client)
    assert client.get("/habits").json()[0]["last_completed"] is None
    add_days(session, h["id"], 5, 3)
    assert client.get("/habits").json()[0]["last_completed"] == days_ago(3)
    r = client.post(f"/habits/{h['id']}/complete")
    assert r.json()["last_completed"] == days_ago(0)
    assert client.delete(f"/habits/{h['id']}/complete").json()["last_completed"] == days_ago(3)


@pytest.mark.parametrize(
    "offsets, expected",
    [([], 0), ([0], 1), ([0, 1, 2, 10, 11], 3), ([20, 19, 18, 17, 5, 4], 4), ([9, 7, 5], 1)],
)
def test_compute_longest_streak(offsets, expected):
    from app.crud import compute_longest_streak

    assert compute_longest_streak({days_ago(n) for n in offsets}) == expected


def test_longest_streak_in_api(client, session):
    h = make_habit(client)
    add_days(session, h["id"], 1, 2, 10, 11, 12, 13)
    item = client.get("/habits").json()[0]
    assert (item["streak"], item["longest_streak"]) == (2, 4)
