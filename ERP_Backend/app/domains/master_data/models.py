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


class Supplier(Base):
    """공급업체(제조사/거래처) 마스터.

    엑셀 원본: 자재리스트 관리 양식.xlsm!제조사리스트, 자재발주현황...xlsm!업체 이름_번호
    """

    __tablename__ = "suppliers"
    __table_args__ = (UniqueConstraint("name", name="uq_suppliers_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tel: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fax: Mapped[str | None] = mapped_column(String(64), nullable=True)
    main_items: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class Material(Base):
    """자재(부품) 마스터.

    엑셀 원본: 자재리스트 관리 양식.xlsm!부품리스트
    """

    __tablename__ = "materials"
    __table_args__ = (
        UniqueConstraint("category", "name", name="uq_materials_category_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)  # 자재품목
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # 자재품명
    manufacturer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supplier_id: Mapped[str | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    usage_note: Mapped[str | None] = mapped_column(Text, nullable=True)  # 자재용도
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class BomComponent(Base):
    """완제품별 BOM 구성.

    엑셀 원본: 자재리스트 관리 양식.xlsm!BOM 관리, PDP 파트리스트 정리.xlsx(시트별 완제품)
    """

    __tablename__ = "bom_components"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_category: Mapped[str | None] = mapped_column(String(120), nullable=True)  # 제품 분류
    product_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # 완제품명
    material_category: Mapped[str | None] = mapped_column(String(120), nullable=True)  # 자재품목
    material_name: Mapped[str] = mapped_column(String(255), nullable=False)  # 자재품명
    material_id: Mapped[str | None] = mapped_column(
        ForeignKey("materials.id", ondelete="SET NULL"), nullable=True, index=True
    )
    manufacturer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)  # Q'ty
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    usage_note: Mapped[str | None] = mapped_column(Text, nullable=True)  # 자재용도/Remark
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_sheet: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_row: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
