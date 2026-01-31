from typing import Annotated, List, Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from task_manager.db_models import User as UserModel, UserRole
from task_manager.schemas.models import User, UserCreate
from task_manager.storage import get_db

router = APIRouter(prefix="/users", tags=["users"])


def _serialize_user(user_model: UserModel) -> User:
    return User.model_validate(
        {
            "id": user_model.id,
            "name": user_model.name,
            "role": user_model.role.value,
        }
    )


@router.get("/", response_model=List[User])
async def list_users(
    role: Annotated[
        Optional[Literal["admin", "manager", "member"]], Query()
    ] = None,
    name: Annotated[Optional[str], Query()] = None,
    db: Session = Depends(get_db),
) -> List[User]:
    stmt = select(UserModel)
    role_value = UserRole(role) if role else None
    if role_value:
        stmt = stmt.where(UserModel.role == role_value)
    if name:
        stmt = stmt.where(UserModel.name == name)
    users = db.execute(stmt).scalars().all()
    return [_serialize_user(user) for user in users]


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    db_user = UserModel(name=user.name, role=UserRole(user.role))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return _serialize_user(db_user)
