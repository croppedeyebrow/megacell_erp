from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, Field


class SalesOrderResponse(BaseModel):
    id: str
    order_no: str
    customer_name: str
    product_name: str
    quantity: float | None = None
    unit: str | None = None
    order_amount: float | None = None
    due_date: str | None = None
    order_date: str | None = None
    status: str
    owner_name: str | None = None
    vendor_name: str | None = None
    memo: str | None = None
    shipped_date: str | None = None
    erp_modified: bool = False

    model_config = {"from_attributes": True}


class SalesOrderListResponse(BaseModel):
    items: list[SalesOrderResponse]
    total: int
    page: int
    page_size: int


class ImportLegacyRequest(BaseModel):
    source_path: str | None = Field(
        default=None,
        description="레거시 megacell.db 경로. 생략 시 기본 경로 탐색.",
    )


class ImportLegacyResponse(BaseModel):
    job_id: str
    status: str
    source_path: str
    success_count: int
    warning_count: int
    fail_count: int
    message: str
    details: dict[str, Any] | None = None


def decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (InvalidOperation, ValueError, TypeError):
        return None
