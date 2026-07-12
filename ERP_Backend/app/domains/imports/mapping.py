from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


def to_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def map_shipment_status_to_code(shipment_status: str | None) -> str:
    text = (shipment_status or "").strip()
    if text in {"출고완료", "완료"}:
        return "completed"
    if text in {"부분출고", "진행", "진행중", "진행 중"}:
        return "in_progress"
    if text in {"취소", "취소됨"}:
        return "cancelled"
    if text in {"지연"}:
        return "delayed"
    if text in {"초안", "미확정"}:
        return "draft"
    # 미출고 및 기타 → 확정(미출고)로 취급
    return "confirmed"


def build_order_no(manufacturing_order_no: str | None, source_key: str, legacy_id: int | None) -> str:
    if manufacturing_order_no and manufacturing_order_no.strip():
        return manufacturing_order_no.strip()
    if legacy_id is not None:
        return f"LEGACY-{legacy_id}"
    return f"LEGACY-{source_key[-24:]}"
