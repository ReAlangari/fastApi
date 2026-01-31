from fastapi import FastAPI
from task_manager.routers import tasks, users
from task_manager.storage import init_db

app = FastAPI(title="Task Management API")

app.include_router(users.router)
app.include_router(tasks.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the Task API"}
