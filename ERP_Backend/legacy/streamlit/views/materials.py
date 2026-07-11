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


def render_materials_bom() -> None:
    st.title("자재/BOM")
    tab_stock, tab_parts, tab_bom = st.tabs(["자재 재고", "부품리스트", "BOM"])

    with tab_stock:
        stock = prepare_numeric(get_table("자재재고"), ["단가", "입고량", "출고량", "현재고", "재고금액"])
        keyword = st.text_input("제조사/자재품목/자재품명 검색", key="material_stock_search")
        filtered = text_filter(stock, keyword, ["제조사", "자재품목", "자재품명"])
        m1, m2, m3 = st.columns(3)
        m1.metric("검색 결과", f"{len(filtered):,}건")
        m2.metric("현재고 합계", metric_sum(filtered, "현재고"))
        m3.metric("재고금액", metric_sum(filtered, "재고금액", "원"))
        table_view(filtered, ["제조사", "자재품목", "자재품명", "단가", "단위", "입고량", "출고량", "현재고", "재고금액"])
        download_csv(filtered, "megacell_material_stock.csv")

    with tab_parts:
        searchable_table(
            "부품리스트",
            "부품리스트",
            "자재품목/자재품명/제조사 검색",
            ["자재품목", "자재품명", "제조사", "자재용도"],
            ["자재품목", "자재품명", "제조사", "단위", "단가", "자재용도"],
            "megacell_parts.csv",
        )

    with tab_bom:
        st.subheader("BOM 관리")
        bom = prepare_numeric(get_table("BOM"), ["소요량", "단가"])

        if bom.empty:
            st.info("BOM 데이터가 없습니다.")
        else:
            c1, c2, c3 = st.columns([1.4, 1.8, 1])
            category_options = safe_unique(bom, "제품 분류")
            selected_category = c1.selectbox("제품분류", category_options, key="bom_category")

            category_bom = bom[bom["제품 분류"].astype(str) == selected_category] if selected_category else bom
            product_options = safe_unique(category_bom, "완제품명")
            selected_product = c2.selectbox("완제품명", product_options, key="bom_product")
            production_qty = c3.number_input("대수", min_value=1, value=1, step=1, key="bom_qty")

            selected_bom = category_bom[
                category_bom["완제품명"].astype(str) == selected_product
            ].copy()

            result = prepare_numeric(selected_bom.copy(), ["소요량", "단가"])
            result["대수"] = production_qty
            if "소요량" in result.columns:
                result["필요수량"] = result["소요량"] * production_qty
            if {"필요수량", "단가"}.issubset(result.columns):
                result["예상금액"] = result["필요수량"] * result["단가"]

            original_col, result_col = st.columns(2, gap="large")
            original_cols = [
                "제품 분류",
                "완제품명",
                "자재품목",
                "자재품명",
                "제조사",
                "단위",
                "소요량",
                "단가",
                "자재용도",
            ]
            result_cols = [
                "자재품목",
                "자재품명",
                "제조사",
                "단위",
                "소요량",
                "대수",
                "필요수량",
                "단가",
                "예상금액",
                "자재용도",
            ]

            with original_col:
                st.markdown("#### BOM 원본")
                with st.container(border=True):
                    st.caption("엑셀 BOM 원장에서 읽어온 1대 기준값입니다.")
                    table_view(selected_bom, original_cols, height=620)

            with result_col:
                st.markdown("#### 대수 반영 결과")
                with st.container(border=True):
                    st.caption(f"{production_qty:,}대 기준으로 계산한 필요수량과 예상금액입니다.")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("자재 항목", f"{len(result):,}개")
                    m2.metric("총 필요수량", metric_sum(result, "필요수량"))
                    m3.metric("예상금액", metric_sum(result, "예상금액", "원"))
                    table_view(result, result_cols, height=520)
                    download_csv(result, "megacell_bom_adjusted.csv")


def render_material_purchases() -> None:
    st.title("자재 발주")
    purchases = prepare_numeric(get_table("발주현황"), ["개수", "단가", "총금액"])

    c1, c2 = st.columns([2, 1.4])
    keyword = c1.text_input("업체명/품목/품명/발주목적 검색")
    status = c2.selectbox("진행 상태", ["전체"] + safe_unique(purchases, "진행 상태"))
    filtered = text_filter(purchases, keyword, ["업체명", "품목", "품명", "발주목적", "비고"])
    if status != "전체" and "진행 상태" in filtered.columns:
        filtered = filtered[filtered["진행 상태"].astype(str) == status]

    m1, m2, m3 = st.columns(3)
    m1.metric("검색 결과", f"{len(filtered):,}건")
    m2.metric("발주 수량", metric_sum(filtered, "개수"))
    m3.metric("총금액", metric_sum(filtered, "총금액", "원"))
    st.divider()
    table_view(
        filtered,
        ["No.", "업체명", "발주일", "입고(요청)일", "발주번호", "품목", "품명", "개수", "단가", "총금액", "발주목적", "진행 상태", "비고"],
    )
    download_csv(filtered, "megacell_purchases.csv")
