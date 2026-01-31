import json
from pathlib import Path

from db_models import (
    Task as TaskModel,
    TaskPriority,
    TaskStatus,
    User as UserModel,
    UserRole,
)
from storage import SessionLocal, init_db

DB_PATH = Path(__file__).resolve().parent / "db.json"


def _normalize_users(users: list[dict]) -> list[dict]:
    next_id = 1
    for user in users:
        if "name" not in user and "username" in user:
            user["name"] = user["username"]
        if "id" in user and isinstance(user["id"], int):
            next_id = max(next_id, user["id"] + 1)
    for user in users:
        if "id" not in user:
            user["id"] = next_id
            next_id += 1
    return users


def _normalize_tasks(tasks: list[dict]) -> list[dict]:
    next_id = 1
    for task in tasks:
        if "name" not in task and "title" in task:
            task["name"] = task["title"]
        if "assigned_user_id" not in task and "assigned_to" in task:
            task["assigned_user_id"] = task["assigned_to"]
        if task.get("description") is None and task.get("name"):
            task["description"] = task.get("name")
        if "id" in task and isinstance(task["id"], int):
            next_id = max(next_id, task["id"] + 1)
    for task in tasks:
        if "id" not in task:
            task["id"] = next_id
            next_id += 1
    return tasks


def migrate() -> None:
    if not DB_PATH.exists():
        print("No db.json file found, skipping migration.")
        return

    with DB_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    users = _normalize_users(data.get("users", []))
    tasks = _normalize_tasks(data.get("tasks", []))

    init_db()

    session = SessionLocal()
    try:
        inserted_users = 0
        for user in users:
            if not user.get("name") or not user.get("role"):
                continue
            existing = session.get(UserModel, user["id"])
            if existing:
                continue
            session.add(
                UserModel(
                    id=user["id"],
                    name=user["name"],
                    role=UserRole(user["role"]),
                )
            )
            inserted_users += 1

        inserted_tasks = 0
        for task in tasks:
            if not task.get("name") or not task.get("status") or not task.get("priority"):
                continue
            if session.get(TaskModel, task["id"]):
                continue
            session.add(
                TaskModel(
                    id=task["id"],
                    name=task["name"],
                    description=task.get("description"),
                    status=TaskStatus(task["status"]),
                    priority=TaskPriority(task["priority"]),
                    assigned_user_id=task.get("assigned_user_id"),
                )
            )
            inserted_tasks += 1

        session.commit()
    finally:
        session.close()

    print(f"Migrated {inserted_users} users and {inserted_tasks} tasks from db.json.")


if __name__ == "__main__":
    migrate()
