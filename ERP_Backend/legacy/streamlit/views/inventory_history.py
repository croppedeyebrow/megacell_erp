from __future__ import annotations

import streamlit as st

from core.db import get_table
from core.ui import (
    download_csv,
    metric_sum,
    prepare_numeric,
    safe_unique,
    table_view,
    text_filter,
)


def render_inventory_history(available_tables: list[str]) -> None:
    st.title("재고 출납기록")
    st.caption("간편재고관리프로그램의 재고정보 시트를 기준으로 입고, 출고, 미출고 변경 이력을 보여줍니다.")

    inventory = prepare_numeric(
        get_table("재고출납"),
        ["입고수량", "출고수량", "미출고수량", "잔고수량"],
    )
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
    m3.metric("미출고수량", metric_sum(filtered, "미출고수량"))
    m4.metric("출고수량", metric_sum(filtered, "출고수량"))

    st.divider()
    table_view(
        filtered,
        [
            "재고정보코드",
            "일자",
            "제품정보코드",
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
