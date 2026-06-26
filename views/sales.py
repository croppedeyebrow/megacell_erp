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


def render_sales_orders() -> None:
    st.title("수주/미출고 현황")
    orders = prepare_numeric(get_table("수주"), ["수량", "단가", "수주금액", "vat포함"])
    if "출고일" in orders.columns:
        shipped_mask = (
            orders["출고일"].notna()
            & ~orders["출고일"].astype(str).str.strip().isin(["", "nan", "NaN", "None", "NaT"])
        )
        orders = orders.copy()
        orders["출고상태"] = "미출고"
        orders.loc[shipped_mask, "출고상태"] = "출고완료"

    c1, c2, c3, c4 = st.columns([2, 2, 1.5, 1.5])
    customer_kw = c1.text_input("납품처/발주처 검색")
    product_kw = c2.text_input("품명/규격 검색")
    instruction_kw = c3.text_input("제조지시서번호 검색")
    order_date_kw = c4.text_input("수주일자 검색")
    c5, c6, c7 = st.columns([1.4, 1.4, 1.4])
    category = c5.selectbox("구분", ["전체"] + safe_unique(orders, "구분"))
    invoice = c6.selectbox("계산서", ["전체"] + safe_unique(orders, "계산서"))
    shipping_status = c7.selectbox("출고상태", ["전체", "미출고", "출고완료"])

    filtered = text_filter(orders, customer_kw, ["납품처", "발주처"])
    filtered = text_filter(filtered, product_kw, ["품명규격", "비고"])
    filtered = text_filter(filtered, instruction_kw, ["제조지시서"])
    filtered = text_filter(filtered, order_date_kw, ["수주일자"])
    if category != "전체" and "구분" in filtered.columns:
        filtered = filtered[filtered["구분"].astype(str) == category]
    if invoice != "전체" and "계산서" in filtered.columns:
        filtered = filtered[filtered["계산서"].astype(str) == invoice]
    if shipping_status != "전체" and "출고상태" in filtered.columns:
        filtered = filtered[filtered["출고상태"].astype(str) == shipping_status]

    shipped_count = int((filtered["출고상태"] == "출고완료").sum()) if "출고상태" in filtered.columns else 0
    pending_count = int((filtered["출고상태"] == "미출고").sum()) if "출고상태" in filtered.columns else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("검색 결과", f"{len(filtered):,}건")
    m2.metric("미출고", f"{pending_count:,}건")
    m3.metric("출고완료", f"{shipped_count:,}건")
    m4.metric("수주금액 합계", metric_sum(filtered, "수주금액", "원"))
    m5.metric("VAT 포함 합계", metric_sum(filtered, "vat포함", "원"))

    st.divider()
    table_view(
        filtered,
        [
            "월",
            "구분",
            "수주일자",
            "출고상태",
            "제조지시서",
            "납품처",
            "품명규격",
            "단위",
            "수량",
            "단가",
            "수주금액",
            "vat포함",
            "발주처",
            "출고요청일",
            "출고일",
            "계산서",
            "비고",
        ],
    )
    download_csv(filtered, "megacell_orders.csv")
