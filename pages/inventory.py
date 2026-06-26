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


def render_current_inventory() -> None:
    st.title("재고 관리")
    inventory = prepare_numeric(get_table("재고"), ["입고수량", "미출고수량", "출고수량", "현재고"])

    c1, c2, c3 = st.columns([2, 1.4, 1.4])
    keyword = c1.text_input("제품명/규격 검색")
    product_type = c2.selectbox("제품분류", ["전체"] + safe_unique(inventory, "제품분류"))
    stock_filter = c3.selectbox("재고 상태", ["전체", "재고 있음", "재고 없음"])

    filtered = text_filter(inventory, keyword, ["제품명", "규격", "유형", "통신카드", "비고"])
    if product_type != "전체" and "제품분류" in filtered.columns:
        filtered = filtered[filtered["제품분류"].astype(str) == product_type]
    if stock_filter == "재고 있음" and "현재고" in filtered.columns:
        filtered = filtered[filtered["현재고"] > 0]
    if stock_filter == "재고 없음" and "현재고" in filtered.columns:
        filtered = filtered[filtered["현재고"] <= 0]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("품목 수", f"{len(filtered):,}개")
    m2.metric("입고수량", metric_sum(filtered, "입고수량"))
    m3.metric("출고수량", metric_sum(filtered, "출고수량"))
    m4.metric("현재고", metric_sum(filtered, "현재고"))

    st.divider()
    table_view(
        filtered,
        [
            "제품분류",
            "제품명",
            "유형",
            "통신카드",
            "규격",
            "입고수량",
            "미출고수량",
            "출고수량",
            "현재고",
            "비고",
        ],
    )
    download_csv(filtered, "megacell_current_inventory.csv")


def render_inventory_history(available_tables: list[str]) -> None:
    st.title("재고 출납기록")
    inventory = prepare_numeric(get_table("재고출납"), ["입고수량", "출고수량", "미출고수량", "잔고수량"])
    if inventory.empty and "재고출납" not in available_tables:
        st.info("재고 출납기록 테이블이 아직 없습니다. 원장 동기화를 한 번 실행해 주세요.")

    c1, c2, c3 = st.columns([2, 1.4, 1.4])
    keyword = c1.text_input("제품명/규격/세부내역 검색")
    product_type = c2.selectbox("제품분류", ["전체"] + safe_unique(inventory, "제품분류"))
    work_type = c3.selectbox("업무구분", ["전체"] + safe_unique(inventory, "업무구분"))

    filtered = text_filter(inventory, keyword, ["제품명", "규격", "세부내역", "비고"])
    if product_type != "전체" and "제품분류" in filtered.columns:
        filtered = filtered[filtered["제품분류"].astype(str) == product_type]
    if work_type != "전체" and "업무구분" in filtered.columns:
        filtered = filtered[filtered["업무구분"].astype(str) == work_type]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("검색 결과", f"{len(filtered):,}건")
    m2.metric("입고수량", metric_sum(filtered, "입고수량"))
    m3.metric("출고수량", metric_sum(filtered, "출고수량"))
    m4.metric("잔고수량", metric_sum(filtered, "잔고수량"))

    st.divider()
    table_view(
        filtered,
        [
            "재고정보코드",
            "일자",
            "제품분류",
            "제품명",
            "유형",
            "통신카드",
            "규격",
            "업무구분",
            "세부내역",
            "입고수량",
            "미출고수량",
            "출고수량",
            "잔고수량",
            "비고",
        ],
    )
    download_csv(filtered, "megacell_inventory_history.csv")
