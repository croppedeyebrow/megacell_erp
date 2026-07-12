"""CLI: 레거시 Streamlit SQLite → 신규 DB 이관

사용 예:
  cd ERP_Backend
  .venv\\Scripts\\activate
  set PYTHONPATH=.
  python -m app.workers.import_legacy_sqlite
  python -m app.workers.import_legacy_sqlite --source \"C:\\path\\to\\megacell.db\"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.core.database import SessionLocal, init_db
from app.domains.imports.service import ImportError, import_legacy_sqlite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import legacy SQLite erp_orders into new DB")
    parser.add_argument(
        "--source",
        help="레거시 megacell.db 절대/상대 경로",
        default=None,
    )
    parser.add_argument("--started-by", default="cli", help="이관 실행자 표시명")
    args = parser.parse_args(argv)

    init_db()
    db = SessionLocal()
    try:
        repo_root = Path(__file__).resolve().parents[2]  # ERP_Backend
        job = import_legacy_sqlite(
            db,
            source_path=args.source,
            started_by=args.started_by,
            repo_root=repo_root,
        )
        print(f"job_id={job.id}")
        print(f"status={job.status}")
        print(f"source={job.source_path}")
        print(f"message={job.message}")
        return 0 if job.status in {"success", "partial_success"} else 1
    except ImportError as exc:
        print(f"ERROR: {exc.message}", file=sys.stderr)
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
