from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.domains.identity.models import User
from app.domains.imports.service import ImportError, import_legacy_sqlite
from app.domains.sales.models import SalesOrder
from app.domains.sales.schemas import (
    ImportLegacyRequest,
    ImportLegacyResponse,
    SalesOrderListResponse,
    SalesOrderResponse,
    decimal_to_float,
)

router = APIRouter(tags=["sales"])


def _to_response(order: SalesOrder) -> SalesOrderResponse:
    return SalesOrderResponse(
        id=order.id,
        order_no=order.order_no,
        customer_name=order.customer_name,
        product_name=order.product_name,
        quantity=decimal_to_float(order.quantity),
        unit=order.unit,
        order_amount=decimal_to_float(order.order_amount),
        due_date=order.due_date,
        order_date=order.order_date,
        status=order.status,
        owner_name=order.owner_name,
        vendor_name=order.vendor_name,
        memo=order.memo,
        shipped_date=order.shipped_date,
        erp_modified=order.erp_modified,
    )


def _require_permission(user: User, permission: str) -> None:
    perms = list(user.permissions or [])
    if permission not in perms and "admin.manage" not in perms:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "권한이 없습니다."},
        )


@router.get("/sales-orders", response_model=SalesOrderListResponse)
def list_sales_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> SalesOrderListResponse:
    _require_permission(user, "sales.view")
    stmt = select(SalesOrder)
    count_stmt = select(func.count()).select_from(SalesOrder)

    if q:
        like = f"%{q.strip()}%"
        filt = or_(
            SalesOrder.order_no.ilike(like),
            SalesOrder.customer_name.ilike(like),
            SalesOrder.product_name.ilike(like),
            SalesOrder.owner_name.ilike(like),
        )
        stmt = stmt.where(filt)
        count_stmt = count_stmt.where(filt)
    if status:
        stmt = stmt.where(SalesOrder.status == status)
        count_stmt = count_stmt.where(SalesOrder.status == status)

    total = int(db.scalar(count_stmt) or 0)
    rows = db.scalars(
        stmt.order_by(SalesOrder.order_date.desc(), SalesOrder.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return SalesOrderListResponse(
        items=[_to_response(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/sales-orders/{order_id}", response_model=SalesOrderResponse)
def get_sales_order(
    order_id: str,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    _require_permission(user, "sales.view")
    order = db.get(SalesOrder, order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "수주를 찾을 수 없습니다."},
        )
    return _to_response(order)


@router.post("/admin/imports/legacy-sqlite", response_model=ImportLegacyResponse)
def run_legacy_sqlite_import(
    body: ImportLegacyRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> ImportLegacyResponse:
    _require_permission(user, "admin.manage")
    try:
        job = import_legacy_sqlite(
            db,
            source_path=body.source_path,
            started_by=user.email,
        )
    except ImportError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "IMPORT_FAILED", "message": exc.message},
        ) from exc

    return ImportLegacyResponse(
        job_id=job.id,
        status=job.status,
        source_path=job.source_path,
        success_count=job.success_count,
        warning_count=job.warning_count,
        fail_count=job.fail_count,
        message=job.message or "",
        details=job.details_json,
    )
