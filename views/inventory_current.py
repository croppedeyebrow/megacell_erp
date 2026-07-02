from __future__ import annotations

import pandas as pd
import streamlit as st

from core.db import get_table
from core.ui import (
    clean_display,
    download_csv,
    metric_sum,
    prepare_numeric,
    safe_unique,
    text_filter,
)


def render_current_inventory_table(df: pd.DataFrame) -> None:
    df = clean_display(df)
    preferred_cols = [
        "제품정보코드",
        "제품분류",
        "제품명",
        "유형",
        "통신카드",
        "규격",
        "재고상태",
        "현재고",
        "미출고수량",
        "입고수량",
        "출고수량",
        "최근출납일",
        "최근업무구분",
        "최근 세부내역",
        "비고",
    ]

    display = df.copy()
    if "현재고" in display.columns:
        stock = pd.to_numeric(display["현재고"], errors="coerce")
        display["재고상태"] = "확인필요"
        display.loc[stock <= 0, "재고상태"] = "재고없음"
        display.loc[(stock > 0) & (stock <= 5), "재고상태"] = "부족"
        display.loc[stock > 5, "재고상태"] = "보유"

    cols = [col for col in preferred_cols if col in display.columns]
    if not cols:
        cols = list(display.columns)
    display = display[cols].copy()

    def highlight_stock(row: pd.Series) -> list[str]:
        styles = [""] * len(row)
        if "현재고" not in row.index:
            return styles

        stock_idx = row.index.get_loc("현재고")
        status_idx = row.index.get_loc("재고상태") if "재고상태" in row.index else None
        stock = pd.to_numeric(row["현재고"], errors="coerce")
        stock_base = (
            "font-weight: 800; text-align: right; "
            "border-left: 3px solid #334155; border-right: 1px solid #334155;"
        )
        status_base = "font-weight: 800; text-align: center;"

        if pd.isna(stock):
            stock_style = stock_base + " background-color: #475569; color: #ffffff;"
            status_style = status_base + " background-color: #64748b; color: #ffffff;"
        elif stock <= 0:
            stock_style = stock_base + " background-color: #b91c1c; color: #ffffff;"
            status_style = status_base + " background-color: #dc2626; color: #ffffff;"
        elif stock <= 5:
            stock_style = stock_base + " background-color: #f59e0b; color: #111827;"
            status_style = status_base + " background-color: #fbbf24; color: #111827;"
        else:
            stock_style = stock_base + " background-color: #15803d; color: #ffffff;"
            status_style = status_base + " background-color: #16a34a; color: #ffffff;"

        styles[stock_idx] = stock_style
        if status_idx is not None:
            styles[status_idx] = status_style
        return styles

    numeric_cols = [
        col
        for col in ["현재고", "미출고수량", "입고수량", "출고수량"]
        if col in display.columns
    ]
    formatter = {col: "{:,.0f}" for col in numeric_cols}
    styled = (
        display.style.apply(highlight_stock, axis=1)
        .format(formatter, na_rep="")
        .set_properties(subset=numeric_cols, **{"text-align": "right"})
    )
    st.dataframe(styled, width="stretch", height=560, hide_index=True)


def add_latest_inventory_detail(inventory: pd.DataFrame) -> pd.DataFrame:
    if inventory.empty or "제품정보코드" not in inventory.columns:
        return inventory

    history = clean_display(get_table("재고출납"))
    if history.empty or "제품정보코드" not in history.columns:
        return inventory

    history = history.copy()
    history["_원본순서"] = range(len(history))
    if "일자" in history.columns:
        history["_일자정렬"] = pd.to_datetime(history["일자"], errors="coerce")
    else:
        history["_일자정렬"] = pd.NaT

    latest = (
        history.sort_values(["제품정보코드", "_일자정렬", "_원본순서"])
        .drop_duplicates("제품정보코드", keep="last")
        .rename(
            columns={
                "일자": "최근출납일",
                "업무구분": "최근업무구분",
                "세부내역": "최근 세부내역",
            }
        )
    )
    latest_cols = [
        col
        for col in ["제품정보코드", "최근출납일", "최근업무구분", "최근 세부내역"]
        if col in latest.columns
    ]
    if len(latest_cols) <= 1:
        return inventory

    return inventory.merge(latest[latest_cols], on="제품정보코드", how="left")


def render_current_inventory() -> None:
    st.title("제품 재고")
    st.caption("간편재고관리프로그램의 제품정보 시트를 기준으로 현재 재고 수량을 보여줍니다.")

    inventory = prepare_numeric(
        get_table("재고"),
        ["입고수량", "출고수량", "미출고수량", "현재고"],
    )
    inventory = add_latest_inventory_detail(inventory)
    type_column = "유형" if "유형" in inventory.columns else "제품분류"

    c1, c2, c3, c4 = st.columns([1.1, 1.4, 2.2, 1.4])
    stock_filter = c1.selectbox("재고 상태", ["전체", "현재고 있음", "현재고 없음", "미출고 있음"])
    selected_categories = c2.multiselect(
        "제품분류",
        safe_unique(inventory, "제품분류"),
        placeholder="제품분류 선택",
        key="inventory_category_filter",
    )

    option_source = inventory
    if selected_categories and "제품분류" in option_source.columns:
        option_source = option_source[option_source["제품분류"].astype(str).isin(selected_categories)]

    selected_products = c3.multiselect(
        "제품명",
        safe_unique(option_source, "제품명"),
        placeholder="제품명 선택",
        key="inventory_product_filter",
    )
    selected_types = c4.multiselect(
        "유형",
        safe_unique(option_source, type_column),
        placeholder="유형 선택",
        key="inventory_type_filter",
    )

    keyword = st.text_input("규격/통신카드/최근 세부내역 보조 검색", key="inventory_keyword")
    filtered = text_filter(
        option_source,
        keyword,
        ["규격", "통신카드", "최근 세부내역", "비고"],
    )
    if selected_products and "제품명" in filtered.columns:
        filtered = filtered[filtered["제품명"].astype(str).isin(selected_products)]
    if selected_types and type_column in filtered.columns:
        filtered = filtered[filtered[type_column].astype(str).isin(selected_types)]
    if stock_filter == "현재고 있음" and "현재고" in filtered.columns:
        filtered = filtered[filtered["현재고"] > 0]
    if stock_filter == "현재고 없음" and "현재고" in filtered.columns:
        filtered = filtered[filtered["현재고"] <= 0]
    if stock_filter == "미출고 있음" and "미출고수량" in filtered.columns:
        filtered = filtered[filtered["미출고수량"] > 0]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("현재고", metric_sum(filtered, "현재고"))
    m2.metric("품목 수", f"{len(filtered):,}개")
    m3.metric("미출고수량", metric_sum(filtered, "미출고수량"))
    m4.metric("입고수량", metric_sum(filtered, "입고수량"))
    m5.metric("출고수량", metric_sum(filtered, "출고수량"))

    st.divider()
    render_current_inventory_table(filtered)
    download_csv(filtered, "megacell_current_inventory.csv")
