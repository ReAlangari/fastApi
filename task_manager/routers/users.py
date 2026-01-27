from typing import Annotated, List, Literal, Optional

from fastapi import APIRouter, Query

from schemas.models import User, UserCreate
from storage import load_db, save_db

router = APIRouter(prefix="/users", tags=["users"])

def _ensure_user_ids(data: dict) -> None:
    updated = False
    users = data.get("users", [])
    next_id = 1
    for user in users:
        if "id" in user and isinstance(user["id"], int):
            next_id = max(next_id, user["id"] + 1)
        if "name" not in user and "username" in user:
            user["name"] = user["username"]
            updated = True
    for user in users:
        if "id" not in user:
            user["id"] = next_id
            next_id += 1
            updated = True
    if updated:
        data["users"] = users
        save_db(data)


@router.get("/", response_model=List[User])
async def list_users(
    role: Annotated[
        Optional[Literal["admin", "manager", "member"]], Query()
    ] = None,
    name: Annotated[Optional[str], Query()] = None,
) -> List[User]:
    data = load_db()
    _ensure_user_ids(data)
    users = [User.model_validate(item) for item in data["users"]]
    results = users
    if role:
        results = [user for user in results if user.role == role]
    if name:
        results = [user for user in results if user.name == name]
    return results


@router.post("/", response_model=User)
async def create_user(user: UserCreate) -> User:
    data = load_db()
    _ensure_user_ids(data)
    users = data["users"]
    next_id = max((u.get("id", 0) for u in users), default=0) + 1
    new_user = User(id=next_id, **user.model_dump())
    users.append(new_user.model_dump())
    save_db(data)
    return new_user
