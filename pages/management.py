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


def render_management_summary() -> None:
    st.title("경영 요약")
    st.caption("현재 적재된 업무 원장 기준의 금액·건수 요약입니다.")

    orders = prepare_numeric(get_table("수주"), ["수량", "수주금액", "vat포함"])
    purchases = prepare_numeric(get_table("발주현황"), ["개수", "단가", "총금액"])
    material_stock = prepare_numeric(get_table("자재재고"), ["현재고", "재고금액"])
    as_history = prepare_numeric(get_table("AS관리"), ["AS비용"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("수주금액", metric_sum(orders, "수주금액", "원"))
    c2.metric("VAT 포함", metric_sum(orders, "vat포함", "원"))
    c3.metric("자재 발주금액", metric_sum(purchases, "총금액", "원"))
    c4.metric("AS 비용", metric_sum(as_history, "AS비용", "원"))

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("월별 수주 요약")
        if orders.empty or "월" not in orders.columns:
            st.info("수주 월 데이터가 없습니다.")
        else:
            monthly = (
                orders.assign(월=orders["월"].astype(str))
                .groupby("월", dropna=False)
                .agg(건수=("월", "size"), 수주금액=("수주금액", "sum"), vat포함=("vat포함", "sum"))
                .reset_index()
                .sort_values("월")
            )
            table_view(monthly, ["월", "건수", "수주금액", "vat포함"], height=360)

    with right:
        st.subheader("거래처별 수주 요약")
        if orders.empty or "납품처" not in orders.columns:
            st.info("납품처 데이터가 없습니다.")
        else:
            by_customer = (
                orders.groupby("납품처", dropna=False)
                .agg(건수=("납품처", "size"), 수주금액=("수주금액", "sum"), vat포함=("vat포함", "sum"))
                .reset_index()
                .sort_values("수주금액", ascending=False)
                .head(30)
            )
            table_view(by_customer, ["납품처", "건수", "수주금액", "vat포함"], height=360)

    st.divider()
    st.subheader("구매·재고 금액 요약")
    summary = pd.DataFrame(
        [
            {"구분": "자재 발주", "건수": len(purchases), "금액": normalize_numeric(purchases.get("총금액", pd.Series(dtype=float))).sum()},
            {"구분": "자재 재고", "건수": len(material_stock), "금액": normalize_numeric(material_stock.get("재고금액", pd.Series(dtype=float))).sum()},
            {"구분": "AS 비용", "건수": len(as_history), "금액": normalize_numeric(as_history.get("AS비용", pd.Series(dtype=float))).sum()},
        ]
    )
    table_view(summary, ["구분", "건수", "금액"], height=220)
    download_csv(summary, "megacell_management_summary.csv")
