import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DOTENV_PATH = BASE_DIR.parent / ".env"

if DOTENV_PATH.exists():
    load_dotenv(DOTENV_PATH)

DEFAULT_SQLITE = BASE_DIR.parent / "task_manager.db"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DEFAULT_SQLITE}",
)

