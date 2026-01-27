from fastapi import FastAPI

from routers import tasks, users

app = FastAPI(title="Task Management API")

app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the Task API"}
