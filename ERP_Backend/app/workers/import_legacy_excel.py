"""CLI: 레거시 엑셀(자재/구매/BOM/2026년 수주) → 신규 DB 적재

사용 예:
  cd ERP_Backend
  .venv\\Scripts\\activate
  set PYTHONPATH=.
  python -m app.workers.import_legacy_excel
  python -m app.workers.import_legacy_excel --data-dir "C:\\path\\to\\data\\legacy_imports"
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.core.database import SessionLocal, init_db
from app.domains.imports.excel_service import run_priority_imports


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import legacy Excel files into new DB")
    parser.add_argument(
        "--data-dir",
        default=None,
        help="data/legacy_imports 경로 (기본: 리포지토리 루트/data/legacy_imports)",
    )
    parser.add_argument("--started-by", default="cli", help="이관 실행자 표시명")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[3]  # workers -> app -> ERP_Backend -> repo root
    data_dir = Path(args.data_dir) if args.data_dir else repo_root / "data" / "legacy_imports"

    init_db()
    db = SessionLocal()
    exit_code = 0
    try:
        jobs = run_priority_imports(db, data_dir=data_dir, started_by=args.started_by)
        for job in jobs:
            print(f"[{job.job_type}] status={job.status} {job.message}")
            if job.status == "failed":
                exit_code = 1
    finally:
        db.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
