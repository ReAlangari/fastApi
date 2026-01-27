from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=50)]
    role: Annotated[Literal["admin", "manager", "member"], Field()]

    model_config = {"extra": "ignore"}


class User(UserCreate):
    id: Annotated[int, Field(ge=1)]


class TaskCreate(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=100)]
    description: Annotated[Optional[str], Field(default=None, max_length=300)]
    status: Annotated[Literal["todo", "in_progress", "done"], Field()]
    priority: Annotated[Literal["low", "medium", "high"], Field()]
    assigned_user_id: Annotated[Optional[int], Field(default=None, ge=1)]

    model_config = {"extra": "ignore"}


class Task(TaskCreate):
    id: Annotated[int, Field(ge=1)]
