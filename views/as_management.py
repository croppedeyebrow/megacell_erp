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


def render_as_management() -> None:
    st.title("AS 관리")
    as_history = prepare_numeric(get_table("AS관리"), ["AS비용"])

    c1, c2 = st.columns([2, 1.4])
    keyword = c1.text_input("접수처/제품명/SN/증상 검색")
    status = c2.selectbox("상태", ["전체"] + safe_unique(as_history, "상태"))
    filtered = text_filter(as_history, keyword, ["접수처", "제품명", "SN", "증상내용", "관리번호"])
    if status != "전체" and "상태" in filtered.columns:
        filtered = filtered[filtered["상태"].astype(str) == status]

    m1, m2, m3 = st.columns(3)
    m1.metric("검색 결과", f"{len(filtered):,}건")
    m2.metric("전체 AS 이력", f"{len(as_history):,}건")
    m3.metric("AS 비용 합계", metric_sum(filtered, "AS비용", "원"))

    st.divider()
    table_view(
        filtered,
        [
            "관리번호",
            "접수일",
            "특수관리",
            "접수처",
            "제품명",
            "SN",
            "수량",
            "증상내용",
            "처리방법",
            "유무상",
            "AS비용",
            "비용처리상태",
            "상태",
            "담당자",
            "출고일",
            "비고",
        ],
    )
    download_csv(filtered, "megacell_as.csv")
