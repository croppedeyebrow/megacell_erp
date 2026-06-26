from __future__ import annotations

import subprocess
import sys

from config import BASE_DIR


def run_db_sync() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BASE_DIR / "init_db.py")],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
