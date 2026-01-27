# Task Management API + Streamlit UI

FastAPI backend for managing users and tasks, with a Streamlit UI for easy interaction.

## Project Structure

```
task_manager/
├── main.py
├── db.json
├── routers/
│   ├── users.py
│   └── tasks.py
└── schemas/
    └── models.py
```

## Requirements

- Python 3.10+

Install dependencies:

```
py -m pip install -r requirements.txt
```

## Run the API

From the `task_manager` directory:

```
py -m uvicorn main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## Run the Streamlit UI

From the `task_manager` directory (in a new terminal):

```
py -m streamlit run streamlit_app.py
```

Streamlit URL is shown in the terminal (usually `http://localhost:8501`).

## Core Endpoints

- `GET /users` — list users
- `POST /users` — create user
- `GET /tasks` — list tasks
- `POST /tasks` — create task

## Data Storage

Data is stored locally in `task_manager/db.json`.
