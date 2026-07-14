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


class MaterialMovement(Base):
    """자재 입출고 내역 (건별 원장).

    현재고는 이 테이블을 자재별로 집계(입고합 - 출고합)해서 계산합니다.
    별도 재고 스냅샷 테이블을 두지 않아 입출고 원장과 현재고가 어긋나지 않게 합니다.

    엑셀 원본: 자재리스트 관리 양식.xlsm!입출고내역
    """

    __tablename__ = "material_movements"
    __table_args__ = (
        UniqueConstraint("source_file", "source_sheet", "source_row", name="uq_material_movements_source"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    moved_at: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)  # 입출고일
    order_no: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # 발주번호
    material_category: Mapped[str | None] = mapped_column(String(120), nullable=True)  # 자재품목
    material_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # 자재품명
    material_id: Mapped[str | None] = mapped_column(
        ForeignKey("materials.id", ondelete="SET NULL"), nullable=True, index=True
    )
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)  # 발주목적/출고목적
    manufacturer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    in_qty: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    out_qty: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    purchase_order_source_key: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )  # 발주연동키 (procurement.purchase_orders.source_key 와 매칭)
    source_file: Mapped[str] = mapped_column(String(255), nullable=False)
    source_sheet: Mapped[str] = mapped_column(String(120), nullable=False)
    source_row: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
