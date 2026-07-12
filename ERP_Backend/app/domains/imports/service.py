from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import utcnow
from app.domains.imports.mapping import (
    build_order_no,
    map_shipment_status_to_code,
    to_decimal,
)
from app.domains.sales.models import ImportJob, SalesOrder, StgErpOrder

DEFAULT_LEGACY_CANDIDATES = [
    Path("legacy/streamlit/instance/megacell.db"),
    Path("ERP_Backend/legacy/streamlit/instance/megacell.db"),
]


class ImportError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def resolve_legacy_db_path(source_path: str | None, repo_root: Path) -> Path:
    if source_path:
        path = Path(source_path).expanduser().resolve()
        if not path.exists():
            raise ImportError(f"레거시 DB 파일을 찾을 수 없습니다: {path}")
        return path

    candidates = [
        repo_root / "legacy" / "streamlit" / "instance" / "megacell.db",
        repo_root / "ERP_Backend" / "legacy" / "streamlit" / "instance" / "megacell.db",
        Path.cwd() / "legacy" / "streamlit" / "instance" / "megacell.db",
        Path.cwd() / "ERP_Backend" / "legacy" / "streamlit" / "instance" / "megacell.db",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    raise ImportError(
        "레거시 megacell.db를 찾을 수 없습니다. "
        "운영 PC의 Streamlit DB를 "
        "ERP_Backend/legacy/streamlit/instance/megacell.db 에 복사하거나 "
        "--source 경로를 지정하세요."
    )


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def import_legacy_sqlite(
    db: Session,
    *,
    source_path: str | None = None,
    started_by: str | None = None,
    repo_root: Path | None = None,
) -> ImportJob:
    root = repo_root or Path(__file__).resolve().parents[3]
    # parents: imports -> domains -> app -> ERP_Backend
    legacy_path = resolve_legacy_db_path(source_path, root)

    job = ImportJob(
        job_type="legacy_sqlite_erp_orders",
        source_path=str(legacy_path),
        status="processing",
        started_by=started_by,
        started_at=utcnow(),
    )
    db.add(job)
    db.flush()

    success = 0
    warnings = 0
    fails = 0
    details: dict[str, Any] = {
        "source_tables": [],
        "errors": [],
    }

    try:
        with sqlite3.connect(str(legacy_path)) as src:
            src.row_factory = sqlite3.Row
            tables = {
                str(r[0])
                for r in src.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            details["source_tables"] = sorted(tables)

            if "erp_orders" not in tables:
                raise ImportError(
                    "레거시 DB에 erp_orders 테이블이 없습니다. "
                    "Streamlit에서 init_db/동기화를 먼저 실행했는지 확인하세요."
                )

            rows = src.execute("SELECT * FROM erp_orders ORDER BY id").fetchall()
            details["erp_orders_source_count"] = len(rows)

            for row in rows:
                try:
                    raw = _row_to_dict(row)
                    source_key = str(raw.get("source_key") or "").strip()
                    if not source_key:
                        fails += 1
                        details["errors"].append(
                            {"legacy_id": raw.get("id"), "error": "source_key 없음"}
                        )
                        continue

                    stg = StgErpOrder(
                        import_job_id=job.id,
                        legacy_id=int(raw["id"]) if raw.get("id") is not None else None,
                        source_table=raw.get("source_table"),
                        source_key=source_key,
                        source_row_id=str(raw.get("source_row_id") or "") or None,
                        manufacturing_order_no=raw.get("manufacturing_order_no"),
                        order_date=raw.get("order_date"),
                        category=raw.get("category"),
                        customer_name=raw.get("customer_name"),
                        vendor_name=raw.get("vendor_name"),
                        product_name=raw.get("product_name"),
                        unit=raw.get("unit"),
                        quantity=to_decimal(raw.get("quantity")),
                        unit_price=to_decimal(raw.get("unit_price")),
                        order_amount=to_decimal(raw.get("order_amount")),
                        vat_amount=to_decimal(raw.get("vat_amount")),
                        invoice_status=raw.get("invoice_status"),
                        shipment_request_date=raw.get("shipment_request_date"),
                        shipped_date=raw.get("shipped_date"),
                        shipment_status=raw.get("shipment_status"),
                        memo=raw.get("memo"),
                        erp_modified=bool(raw.get("erp_modified") or 0),
                        source_payload_json=raw.get("source_payload_json"),
                        source_synced_at=raw.get("source_synced_at"),
                        legacy_created_at=raw.get("created_at"),
                        legacy_updated_at=raw.get("updated_at"),
                        legacy_updated_by=raw.get("updated_by"),
                        raw_json={k: (str(v) if v is not None else None) for k, v in raw.items()},
                    )
                    db.add(stg)

                    existing = db.scalar(
                        select(SalesOrder).where(SalesOrder.source_key == source_key)
                    )
                    order_no = build_order_no(
                        raw.get("manufacturing_order_no"),
                        source_key,
                        int(raw["id"]) if raw.get("id") is not None else None,
                    )
                    status = map_shipment_status_to_code(raw.get("shipment_status"))

                    if existing and existing.erp_modified:
                        # 신규 원장에서 이미 수정된 건은 덮어쓰지 않음
                        warnings += 1
                        continue

                    payload = {
                        "order_no": order_no,
                        "source_key": source_key,
                        "legacy_id": int(raw["id"]) if raw.get("id") is not None else None,
                        "order_date": raw.get("order_date") or None,
                        "category": raw.get("category") or None,
                        "customer_name": (raw.get("customer_name") or "").strip(),
                        "vendor_name": raw.get("vendor_name") or None,
                        "product_name": (raw.get("product_name") or "").strip(),
                        "unit": raw.get("unit") or None,
                        "quantity": to_decimal(raw.get("quantity")),
                        "unit_price": to_decimal(raw.get("unit_price")),
                        "order_amount": to_decimal(raw.get("order_amount")),
                        "vat_amount": to_decimal(raw.get("vat_amount")),
                        "invoice_status": raw.get("invoice_status") or None,
                        "due_date": raw.get("shipment_request_date") or None,
                        "shipped_date": raw.get("shipped_date") or None,
                        "status": status,
                        "memo": raw.get("memo") or None,
                        "erp_modified": bool(raw.get("erp_modified") or 0),
                        "owner_name": raw.get("updated_by") or None,
                    }

                    if existing:
                        for key, value in payload.items():
                            setattr(existing, key, value)
                        existing.version = int(existing.version or 1) + 1
                    else:
                        # order_no 충돌 시 suffix
                        clash = db.scalar(
                            select(SalesOrder).where(SalesOrder.order_no == order_no)
                        )
                        if clash and clash.source_key != source_key:
                            payload["order_no"] = f"{order_no}-{raw.get('id')}"
                            warnings += 1
                        db.add(SalesOrder(**payload))

                    success += 1
                except Exception as exc:  # noqa: BLE001 — 행 단위 오류 수집
                    fails += 1
                    details["errors"].append(
                        {
                            "legacy_id": row["id"] if "id" in row.keys() else None,
                            "error": str(exc),
                        }
                    )

        job.status = "partial_success" if fails or warnings else "success"
        if fails and success == 0:
            job.status = "failed"
        job.success_count = success
        job.warning_count = warnings
        job.fail_count = fails
        job.message = (
            f"erp_orders {details.get('erp_orders_source_count', 0)}건 중 "
            f"반영 {success} / 경고 {warnings} / 실패 {fails}"
        )
        job.details_json = details
        job.ended_at = utcnow()
        db.commit()
        db.refresh(job)
        return job
    except Exception as exc:
        job.status = "failed"
        job.fail_count = fails or 1
        job.success_count = success
        job.warning_count = warnings
        job.message = str(exc)
        job.details_json = details
        job.ended_at = utcnow()
        db.commit()
        db.refresh(job)
        if isinstance(exc, ImportError):
            raise
        raise ImportError(str(exc)) from exc
