from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("MEGACELL_DATA_DIR", BASE_DIR / "data")).resolve()
INSTANCE_DIR = Path(os.getenv("MEGACELL_INSTANCE_DIR", BASE_DIR / "instance")).resolve()
LOG_DIR = Path(os.getenv("MEGACELL_LOG_DIR", BASE_DIR / "logs")).resolve()
DB_PATH = Path(os.getenv("MEGACELL_DB_PATH", INSTANCE_DIR / "megacell.db")).resolve()
BATTERY_EXPORT_DIR = INSTANCE_DIR / "battery_exports"


def ensure_runtime_dirs() -> None:
    for path in [DATA_DIR, INSTANCE_DIR, LOG_DIR, BATTERY_EXPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)
