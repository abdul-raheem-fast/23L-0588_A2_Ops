import os
from pathlib import Path


def _database_uri(value: str) -> str:
    if value.startswith("sqlite:///"):
        database_path = Path(value.removeprefix("sqlite:///"))
        if not database_path.is_absolute():
            database_path = Path.cwd() / database_path
        database_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{database_path}"
    return value


class Settings:
    model_path = Path(os.getenv("MODEL_PATH", "models/champion.keras"))
    model_name = os.getenv("MODEL_NAME", "visionguard-champion")
    model_version = os.getenv("MODEL_VERSION", "1")
    threshold = float(os.getenv("DECISION_THRESHOLD", "0.5"))
    database_url = _database_uri(os.getenv("DATABASE_URL", "sqlite:///data/visionguard.db"))
    max_content_length = int(os.getenv("MAX_CONTENT_LENGTH", str(10 * 1024 * 1024)))
    allowed_extensions = {"jpg", "jpeg", "png", "webp"}

