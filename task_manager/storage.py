import json
from pathlib import Path
from typing import Any, Dict

DB_PATH = Path(__file__).resolve().parent / "db.json"


def load_db() -> Dict[str, list]:
    if not DB_PATH.exists():
        return {"users": [], "tasks": []}
    with DB_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    data.setdefault("users", [])
    data.setdefault("tasks", [])
    return data


def save_db(data: Dict[str, Any]) -> None:
    with DB_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=True, indent=2)
