"""Application configuration for the AI finance analyzer."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "db.sqlite3"
ML_MODELS_DIR = PROJECT_ROOT / "ml_models"
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
SAMPLE_DATA_PATH = DATA_DIR / "sample_data.csv"

PASSWORD_SALT_BYTES = 16
PBKDF2_ITERATIONS = 100_000
MIN_PASSWORD_LENGTH = 8
DEFAULT_MONTHLY_INCOME = 60000.0
APP_NAME = "AI Financial Intelligence & Advisory System"


def ensure_directories() -> None:
    """Create required runtime directories if they do not exist."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
