from typing import Annotated, List, Literal, Optional

from fastapi import APIRouter, Query

from schemas.models import Task, TaskCreate
from storage import load_db, save_db

router = APIRouter(prefix="/tasks", tags=["tasks"])

def _normalize_tasks(data: dict) -> None:
    updated = False
    tasks = data.get("tasks", [])
    next_id = 1
    for task in tasks:
        if "id" in task and isinstance(task["id"], int):
            next_id = max(next_id, task["id"] + 1)
        if "assigned_user_id" not in task and "assigned_to" in task:
            task["assigned_user_id"] = task.get("assigned_to")
            updated = True
        if "name" not in task and "title" in task:
            task["name"] = task.get("title")
            updated = True
        if task.get("description") is None and task.get("name"):
            task["description"] = task.get("name")
            updated = True
    for task in tasks:
        if "id" not in task:
            task["id"] = next_id
            next_id += 1
            updated = True
    if updated:
        data["tasks"] = tasks
        save_db(data)


@router.get("/", response_model=List[Task])
async def list_tasks(
    status: Annotated[
        Optional[Literal["todo", "in_progress", "done"]], Query()
    ] = None,
    priority: Annotated[
        Optional[Literal["low", "medium", "high"]], Query()
    ] = None,
    assigned_user_id: Annotated[Optional[int], Query(ge=1)] = None,
) -> List[Task]:
    data = load_db()
    _normalize_tasks(data)
    tasks = [Task.model_validate(item) for item in data["tasks"]]
    results = tasks
    if status:
        results = [task for task in results if task.status == status]
    if priority:
        results = [task for task in results if task.priority == priority]
    if assigned_user_id is not None:
        results = [
            task for task in results if task.assigned_user_id == assigned_user_id
        ]
    return results


@router.post("/", response_model=Task)
async def create_task(task: TaskCreate) -> Task:
    data = load_db()
    _normalize_tasks(data)
    tasks = data["tasks"]
    next_id = max((t.get("id", 0) for t in tasks), default=0) + 1
    new_task = Task(id=next_id, **task.model_dump())
    tasks.append(new_task.model_dump())
    save_db(data)
    return new_task
