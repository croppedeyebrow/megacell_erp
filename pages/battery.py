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


def render_battery_management() -> None:
    st.title("배터리 관리")
    stock = prepare_numeric(get_table("배터리재고"), ["입고", "출고", "미출고", "재고"])
    transactions = prepare_numeric(get_table("배터리입출고"), ["단가", "수량", "금액"])
    items = prepare_numeric(get_table("배터리품목"), ["단가"])
    usage_log = get_table("배터리사용이력")

    if stock.empty and transactions.empty and items.empty and usage_log.empty:
        st.info("배터리 데이터가 아직 DB에 적재되지 않았습니다. `python init_db.py`를 다시 실행해 주세요.")
        st.stop()

    tab_stock, tab_history, tab_schedule, tab_items, tab_log = st.tabs(
        ["현재고", "입출고 이력", "미출고 달력", "품목관리", "사용이력"]
    )

    with tab_stock:
        keyword = st.text_input("품목명 검색", key="battery_stock_search")
        filtered = text_filter(stock, keyword, ["품목명"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("품목 수", f"{len(filtered):,}개")
        c2.metric("입고", metric_sum(filtered, "입고"))
        c3.metric("출고", metric_sum(filtered, "출고"))
        c4.metric("재고", metric_sum(filtered, "재고"))
        table_view(filtered, ["품목명", "입고", "출고", "미출고", "재고"])
        download_csv(filtered, "megacell_battery_stock.csv")

    with tab_history:
        c1, c2 = st.columns([2, 1.3])
        keyword = c1.text_input("품목명/메모/주문서 번호 검색", key="battery_history_search")
        kind = c2.selectbox("구분", ["전체"] + safe_unique(transactions, "구분"))
        filtered = text_filter(transactions, keyword, ["품목명", "메모", "주문서 번호", "품목코드"])
        if kind != "전체" and "구분" in filtered.columns:
            filtered = filtered[filtered["구분"].astype(str) == kind]
        m1, m2, m3 = st.columns(3)
        m1.metric("검색 결과", f"{len(filtered):,}건")
        m2.metric("수량 합계", metric_sum(filtered, "수량"))
        m3.metric("금액 합계", metric_sum(filtered, "금액", "원"))
        table_view(
            filtered,
            ["ID", "작성일자", "구분", "출고일자", "품목코드", "품목명", "단가", "수량", "금액", "메모", "주문서 번호"],
        )
        download_csv(filtered, "megacell_battery_transactions.csv")

    with tab_schedule:
        pending = build_pending_battery(transactions)
        parsed_months = sorted([value for value in pending.get("년월", pd.Series(dtype=str)).unique() if value])
        default_month = date.today().strftime("%Y-%m")
        default_index = parsed_months.index(default_month) if default_month in parsed_months else 0

        c1, c2 = st.columns([1.2, 2])
        month_key = c1.selectbox(
            "월",
            parsed_months,
            index=default_index if parsed_months else None,
            key="battery_pending_month",
        )
        keyword = c2.text_input("품목명/메모/주문서 번호 검색", key="battery_pending_search")

        filtered = text_filter(pending, keyword, ["품목명", "메모", "주문서 번호", "품목코드"])
        m1, m2, m3 = st.columns(3)
        m1.metric("미출고", f"{len(filtered):,}건")
        m2.metric("수량 합계", metric_sum(filtered, "수량"))
        m3.metric("금액 합계", metric_sum(filtered, "금액", "원"))

        st.divider()
        render_pending_calendar(filtered, month_key)

        unscheduled = filtered[filtered["달력일자"].isna()].copy()
        if not unscheduled.empty:
            st.divider()
            st.subheader("일정 미확정")
            table_view(
                unscheduled,
                ["ID", "작성일자", "출고일자", "품목코드", "품목명", "수량", "금액", "메모", "주문서 번호"],
                height=260,
            )

        st.divider()
        st.subheader("미출고 목록")
        table_view(
            filtered,
            ["ID", "작성일자", "출고일자", "품목코드", "품목명", "수량", "금액", "메모", "주문서 번호"],
            height=360,
        )
        download_csv(filtered, "megacell_battery_pending.csv")

    with tab_items:
        keyword = st.text_input("품목코드/품목명 검색", key="battery_items_search")
        filtered = text_filter(items, keyword, ["품목코드", "품목명"])
        st.metric("품목 수", f"{len(filtered):,}개")
        table_view(filtered, ["품목코드", "품목명", "단가"])
        download_csv(filtered, "megacell_battery_items.csv")

    with tab_log:
        keyword = st.text_input("작업 내역 검색", key="battery_log_search")
        filtered = text_filter(usage_log, keyword, ["구분", "작업 내역 상세"])
        st.metric("사용이력", f"{len(filtered):,}건")
        table_view(filtered, ["일시", "구분", "작업 내역 상세"])
        download_csv(filtered, "megacell_battery_usage_log.csv")
