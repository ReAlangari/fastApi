# Task Management API + Streamlit UI

Lightweight FastAPI backend + Streamlit dashboard for managing users and tasks in one place.

## Features

- Async FastAPI endpoints for users and tasks, with SQLAlchemy/SQLite persistence by default.
- Streamlit UX for viewing the Kanban board, creating tasks, and managing the team.
- Built-in migration script to move legacy `db.json` data into the SQL database.

## Getting Started

1. Install the dependencies:

   ```
   py -m pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and optionally set `DATABASE_URL`. The app defaults to a local `sqlite:///task_manager.db` file when the variable is missing.

3. (Optional) Migrate JSON payloads into the database:

   ```
   py -m task_manager.migrate_json_to_db
   ```

## Running the API

Run from the repository root so imports resolve:

```
py -m uvicorn task_manager.main:app --reload
```

Once the server is running, the OpenAPI docs are available at `http://127.0.0.1:8000/docs`.

## Running the Streamlit UI

In a separate terminal, point Streamlit to the same host:

```
py -m streamlit run task_manager/streamlit_app.py
```

Use the sidebar to update the API base URL if you run the backend on a different port.

## API Endpoints

- `GET /users/` — list users
- `POST /users/` — create a user
- `GET /tasks/` — list tasks with optional filters
- `POST /tasks/` — create a task

## Database Notes

- Uses SQLAlchemy models in `task_manager/db_models.py`. Tables are created automatically on startup.
- Defaults to `sqlite:///task_manager.db` for local development; set `DATABASE_URL` for PostgreSQL or other engines.
- Legacy `task_manager/db.json` is left as a backup after running `task_manager/migrate_json_to_db.py`.
