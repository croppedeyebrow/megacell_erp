from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from config import BASE_DIR
from core.db import get_table
from core.ui import (
    clean_display,
    download_csv,
    metric_sum,
    normalize_numeric,
    prepare_numeric,
    safe_unique,
    searchable_table,
    table_view,
    text_filter,
)
from services.battery_service import build_pending_battery, render_pending_calendar
from services.document_service import (
    build_order_workbook_bytes,
    extract_document_pdf,
    safe_filename,
)


def render_dashboard() -> None:
    st.title("대시보드")
    st.caption("현재 DB에 적재된 업무 원장 기준 요약입니다.")

    orders = prepare_numeric(get_table("수주"), ["수량", "단가", "수주금액", "vat포함"])
    inventory_stock = prepare_numeric(get_table("재고"), ["입고수량", "출고수량", "미출고수량", "현재고"])
    as_history = prepare_numeric(get_table("AS관리"), ["AS비용"])
    material_stock = prepare_numeric(get_table("자재재고"), ["입고량", "출고량", "현재고", "재고금액"])
    purchases = prepare_numeric(get_table("발주현황"), ["개수", "단가", "총금액"])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("수주", f"{len(orders):,}건")
    col2.metric("수주금액", metric_sum(orders, "수주금액", "원"))
    col3.metric("제품 현재고", metric_sum(inventory_stock, "현재고"))
    col4.metric("자재 현재고", metric_sum(material_stock, "현재고"))
    col5.metric("AS 이력", f"{len(as_history):,}건")

    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader("최근 수주")
        table_view(
            orders.tail(12).iloc[::-1],
            ["수주일자", "납품처", "품명규격", "수량", "수주금액", "출고일", "계산서"],
            height=360,
        )
    with right:
        st.subheader("최근 자재 발주")
        table_view(
            purchases.tail(12).iloc[::-1],
            ["업체명", "발주일", "입고(요청)일", "품목", "품명", "개수", "진행 상태"],
            height=360,
        )
