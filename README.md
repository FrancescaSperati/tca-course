# Habit tracker

FastAPI + SQLite backend (`backend/`, managed with uv) and a React + TypeScript + Vite frontend (`frontend/`).

```
make setup   # installs uv (if missing), checks Node 20+, installs backend and frontend deps
make dev     # API on :8000, app on :5173 (Vite proxies /api/* to the API, so no CORS)
make test    # pytest + TypeScript type-check
```

API docs: http://localhost:8000/docs. The SQLite file lives at `backend/habits.db` and is seeded with eat, drink and read on first start.

`frontend/.npmrc` pins the public npm registry for this project.
