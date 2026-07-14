from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.security import utcnow


def _uuid() -> str:
    return str(uuid.uuid4())


class PurchaseOrder(Base):
    """자재 발주.

    엑셀 원본: 자재발주현황_발주서 통합 양식.xlsm!발주현황
    """

    __tablename__ = "purchase_orders"
    __table_args__ = (
        UniqueConstraint("source_key", name="uq_purchase_orders_source_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    seq_no: Mapped[int | None] = mapped_column(Integer, nullable=True)  # No.
    order_no: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # 발주번호
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    supplier_id: Mapped[str | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    order_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(32), nullable=True)  # 입고(요청)일
    material_category: Mapped[str | None] = mapped_column(String(120), nullable=True)  # 품목
    material_name: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 품명
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)  # 발주목적
    status: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 진행 상태 (원문 그대로)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)  # 발주연동키
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_row: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
