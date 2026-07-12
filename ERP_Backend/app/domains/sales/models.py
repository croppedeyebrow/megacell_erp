from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.core.database import Base
from app.core.security import utcnow


def _uuid() -> str:
    return str(uuid.uuid4())


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    job_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    started_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    details_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class StgErpOrder(Base):
    """레거시 SQLite erp_orders 원본 보존용 staging."""

    __tablename__ = "stg_erp_orders"
    __table_args__ = (UniqueConstraint("import_job_id", "source_key", name="uq_stg_erp_orders_job_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    import_job_id: Mapped[str] = mapped_column(ForeignKey("import_jobs.id", ondelete="CASCADE"), index=True)
    legacy_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_table: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_row_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    manufacturing_order_no: Mapped[str | None] = mapped_column(String(120), nullable=True)
    order_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    order_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    vat_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    invoice_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    shipment_request_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    shipped_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    shipment_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    erp_modified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_synced_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    legacy_created_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    legacy_updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    legacy_updated_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SalesOrder(Base):
    """신규 시스템 수주 운영 원장."""

    __tablename__ = "sales_orders"
    __table_args__ = (UniqueConstraint("source_key", name="uq_sales_orders_source_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    order_no: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    source_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    legacy_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    order_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    order_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    vat_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    invoice_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    shipped_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="confirmed", index=True)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    erp_modified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    owner_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
