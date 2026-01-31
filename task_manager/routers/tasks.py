from typing import Annotated, List, Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from task_manager.db_models import Task as TaskModel, TaskPriority, TaskStatus
from task_manager.schemas.models import Task, TaskCreate
from task_manager.storage import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _serialize_task(task_model: TaskModel) -> Task:
    return Task.model_validate(
        {
            "id": task_model.id,
            "name": task_model.name,
            "description": task_model.description,
            "status": task_model.status.value,
            "priority": task_model.priority.value,
            "assigned_user_id": task_model.assigned_user_id,
        }
    )


@router.get("/", response_model=List[Task])
async def list_tasks(
    status: Annotated[
        Optional[Literal["todo", "in_progress", "done"]], Query()
    ] = None,
    priority: Annotated[
        Optional[Literal["low", "medium", "high"]], Query()
    ] = None,
    assigned_user_id: Annotated[Optional[int], Query(ge=1)] = None,
    db: Session = Depends(get_db),
) -> List[Task]:
    stmt = select(TaskModel)
    status_value = TaskStatus(status) if status else None
    priority_value = TaskPriority(priority) if priority else None
    if status_value:
        stmt = stmt.where(TaskModel.status == status_value)
    if priority_value:
        stmt = stmt.where(TaskModel.priority == priority_value)
    if assigned_user_id is not None:
        stmt = stmt.where(TaskModel.assigned_user_id == assigned_user_id)
    tasks = db.execute(stmt).scalars().all()
    return [_serialize_task(task) for task in tasks]


@router.post("/", response_model=Task)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
) -> Task:
    db_task = TaskModel(
        name=task.name,
        description=task.description,
        status=TaskStatus(task.status),
        priority=TaskPriority(task.priority),
        assigned_user_id=task.assigned_user_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return _serialize_task(db_task)
