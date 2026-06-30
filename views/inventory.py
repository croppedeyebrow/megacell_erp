from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from core.db import get_table
from core.ui import (
    clean_display,
    download_csv,
    metric_sum,
    prepare_numeric,
    safe_unique,
    table_view,
    text_filter,
)


LEGACY_MATERIAL_PATH = Path(r"\\MegaCell_NAS\경영지원팀\이재성주임\이전버전 파일 관리\자재관리.xlsm")


@st.cache_data(show_spinner=False)
def load_legacy_material_demand(path_text: str) -> pd.DataFrame:
    path = Path(path_text)
    if not path.exists():
        return pd.DataFrame()

    try:
        legacy = pd.read_excel(path, sheet_name="입출고관리", header=2, engine="openpyxl")
    except Exception:
        return pd.DataFrame()

    legacy = legacy.rename(columns=lambda col: "" if pd.isna(col) else str(col).strip())
    required = ["일자", "코드", "품목", "규격", "입고수량", "출고수량", "거래처"]
    if not all(col in legacy.columns for col in required):
        return pd.DataFrame()

    legacy = legacy[required].copy()
    legacy = legacy[legacy["일자"].astype(str).str.strip() != "일자"]
    legacy["일자"] = pd.to_datetime(legacy["일자"], errors="coerce")
    legacy = legacy[legacy["일자"].notna()].copy()
    legacy = legacy[legacy["일자"] < pd.Timestamp("2026-05-01")]
    if legacy.empty:
        return pd.DataFrame()

    for col in ["입고수량", "출고수량"]:
        legacy[col] = pd.to_numeric(
            legacy[col].astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce",
        ).fillna(0)

    result = pd.DataFrame(
        {
            "일자": legacy["일자"],
            "제품정보코드": legacy["코드"].astype(str).str.strip(),
            "제품분류": legacy["품목"].astype(str).str.strip(),
            "제품명": legacy["규격"].astype(str).str.strip(),
            "규격": "",
            "업무구분": "과거 입출고",
            "세부내역": legacy["거래처"].astype(str).str.strip(),
            "입고수량": legacy["입고수량"],
            "출고수량": legacy["출고수량"],
            "미출고수량": 0,
            "잔고수량": pd.NA,
            "비고": "자재관리.xlsm",
            "자료원": "5월 이전 자재관리",
        }
    )
    return result.reset_index(drop=True)


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
        ["입고수량", "미출고수량", "출고수량", "현재고"],
    )
    inventory = add_latest_inventory_detail(inventory)

    c1, c2, c3 = st.columns([2, 1.4, 1.4])
    keyword = c1.text_input("제품명/규격/최근 세부내역 검색")
    product_type = c2.selectbox("제품분류", ["전체"] + safe_unique(inventory, "제품분류"))
    stock_filter = c3.selectbox("현재고 상태", ["전체", "현재고 있음", "현재고 없음", "미출고 있음"])

    filtered = text_filter(
        inventory,
        keyword,
        ["제품명", "규격", "유형", "통신카드", "최근 세부내역", "비고"],
    )
    if product_type != "전체" and "제품분류" in filtered.columns:
        filtered = filtered[filtered["제품분류"].astype(str) == product_type]
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


def render_inventory_demand_analysis() -> None:
    st.title("수요량 분석")
    st.caption("재고 출납기록의 출고수량과 미출고수량을 기준으로 제품별 수요 흐름을 분석합니다.")

    history = prepare_numeric(
        get_table("재고출납"),
        ["입고수량", "출고수량", "미출고수량", "잔고수량"],
    )
    if history.empty:
        st.info("분석할 재고 출납기록이 없습니다. 원장 동기화를 먼저 실행해 주세요.")
        return

    df = history.copy()
    df["자료원"] = "현재 원장"
    include_legacy = st.checkbox("5월 이전 자재관리 자료 포함", value=True)
    if include_legacy:
        legacy = load_legacy_material_demand(str(LEGACY_MATERIAL_PATH))
        if legacy.empty:
            st.caption("5월 이전 자재관리 자료를 찾지 못했거나 읽을 수 없습니다.")
        else:
            df = pd.concat([df, legacy], ignore_index=True, sort=False)

    if "일자" in df.columns:
        df["분석일자"] = pd.to_datetime(df["일자"], errors="coerce")
    else:
        df["분석일자"] = pd.NaT
    df = df[df["분석일자"].notna()].copy()
    if df.empty:
        st.info("날짜가 인식되는 재고 출납기록이 없어 수요량을 월별로 분석할 수 없습니다.")
        return

    df["분석월"] = df["분석일자"].dt.to_period("M").astype(str)

    c1, c2 = st.columns([1.4, 1.4])
    product_type = c1.selectbox("제품분류", ["전체"] + safe_unique(df, "제품분류"))
    demand_basis = c2.selectbox("수요량 기준", ["출고+미출고", "출고수량", "미출고수량"])

    min_date = df["분석일자"].min().date()
    max_date = df["분석일자"].max().date()
    default_start = max(df["분석일자"].min(), df["분석일자"].max() - pd.Timedelta(days=365)).date()
    d1, d2 = st.columns(2)
    start_date = d1.date_input(
        "시작일",
        value=default_start,
        min_value=min_date,
        max_value=max_date,
    )
    end_date = d2.date_input(
        "종료일",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
    )
    if start_date > end_date:
        st.warning("시작일이 종료일보다 늦어 날짜 범위를 자동으로 바꿔 적용했습니다.")
        start_date, end_date = end_date, start_date
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)

    filtered = df.copy()
    if product_type != "전체" and "제품분류" in filtered.columns:
        filtered = filtered[filtered["제품분류"].astype(str) == product_type]
    filtered = filtered[
        (filtered["분석일자"] >= start_ts)
        & (filtered["분석일자"] <= end_ts)
    ]

    product_label_cols = [col for col in ["제품정보코드", "제품명", "규격"] if col in filtered.columns]
    if product_label_cols:
        product_items = (
            filtered[product_label_cols]
            .drop_duplicates()
            .fillna("")
            .astype(str)
        )
        product_items["제품선택"] = product_items.apply(
            lambda row: " | ".join(value for value in row.tolist() if value and value != "nan"),
            axis=1,
        )
        product_options = sorted(value for value in product_items["제품선택"].unique() if value)
        selected_products = st.multiselect(
            "제품 선택(복수 선택 가능)",
            product_options,
            placeholder="선택하지 않으면 전체 제품을 분석합니다.",
        )
        if selected_products:
            st.caption(f"선택한 {len(selected_products):,}개 품목의 수요량을 합산해 분석합니다.")
            filtered = filtered.copy()
            label_frame = filtered[product_label_cols].fillna("").astype(str)
            filtered["제품선택"] = label_frame.apply(
                lambda row: " | ".join(value for value in row.tolist() if value and value != "nan"),
                axis=1,
            )
            filtered = filtered[filtered["제품선택"].isin(selected_products)]
        else:
            st.caption("품목을 선택하지 않아 현재 조건의 전체 품목을 합산해 분석합니다.")
    else:
        st.info("제품 선택에 사용할 제품정보코드, 제품명, 규격 컬럼이 없습니다.")

    if demand_basis == "출고수량":
        filtered["수요량"] = filtered["출고수량"]
    elif demand_basis == "미출고수량":
        filtered["수요량"] = filtered["미출고수량"]
    else:
        filtered["수요량"] = filtered["출고수량"] + filtered["미출고수량"]

    filtered = filtered[filtered["수요량"] != 0].copy()
    if filtered.empty:
        st.info("선택한 조건에 해당하는 수요량 데이터가 없습니다.")
        return

    product_keys = [col for col in ["제품정보코드", "제품분류", "제품명", "규격"] if col in filtered.columns]
    item_count = filtered[product_keys].drop_duplicates().shape[0] if product_keys else 0
    monthly = (
        filtered.groupby("분석월", as_index=False)
        .agg(수요량=("수요량", "sum"), 출고수량=("출고수량", "sum"), 미출고수량=("미출고수량", "sum"))
        .sort_values("분석월")
    )
    monthly_average = monthly["수요량"].mean() if not monthly.empty else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("수요량 합계", f"{filtered['수요량'].sum():,.0f}")
    m2.metric("월평균 수요", f"{monthly_average:,.1f}")
    m3.metric("대상 품목", f"{item_count:,}개")
    m4.metric("분석 기록", f"{len(filtered):,}건")
    if "자료원" in filtered.columns:
        source_summary = filtered["자료원"].fillna("기타").value_counts()
        st.caption(" / ".join(f"{name} {count:,}건" for name, count in source_summary.items()))

    st.divider()
    left, right = st.columns([1.05, 1])
    with left:
        st.subheader("월별 수요량")
        chart_data = monthly.set_index("분석월")[["수요량"]]
        st.bar_chart(chart_data, height=280)
        table_view(monthly, ["분석월", "수요량", "출고수량", "미출고수량"], height=260)

    with right:
        st.subheader("제품별 수요 상위")
        group_cols = [col for col in ["제품정보코드", "제품분류", "제품명", "규격"] if col in filtered.columns]
        by_product = (
            filtered.groupby(group_cols, dropna=False, as_index=False)
            .agg(수요량=("수요량", "sum"), 출고수량=("출고수량", "sum"), 미출고수량=("미출고수량", "sum"))
            .sort_values("수요량", ascending=False)
        )
        table_view(
            by_product.head(20),
            ["제품정보코드", "제품분류", "제품명", "규격", "수요량", "출고수량", "미출고수량"],
            height=560,
        )

    st.divider()
    st.subheader("현재고 대비 수요")
    stock = prepare_numeric(get_table("재고"), ["현재고", "미출고수량"])
    if not stock.empty and "제품정보코드" in stock.columns and "제품정보코드" in by_product.columns:
        stock_cols = [
            col
            for col in ["제품정보코드", "현재고", "미출고수량"]
            if col in stock.columns
        ]
        demand_stock = by_product.merge(stock[stock_cols], on="제품정보코드", how="left", suffixes=("", "_현재"))
        month_count = max(1, len(monthly["분석월"].unique()))
        demand_stock["월평균수요"] = demand_stock["수요량"] / month_count
        demand_stock["예상소진개월"] = demand_stock.apply(
            lambda row: row["현재고"] / row["월평균수요"] if row["월평균수요"] > 0 else pd.NA,
            axis=1,
        )
        demand_stock = demand_stock.sort_values(["예상소진개월", "수요량"], ascending=[True, False])
        table_view(
            demand_stock,
            [
                "제품정보코드",
                "제품분류",
                "제품명",
                "규격",
                "현재고",
                "월평균수요",
                "예상소진개월",
                "수요량",
                "출고수량",
                "미출고수량",
            ],
            height=520,
        )

        st.divider()
        st.subheader("적정재고 분석")
        a1, a2 = st.columns([1.2, 1.2])
        lead_time_days = a1.number_input(
            "리드타임(일)",
            min_value=1,
            max_value=365,
            value=12,
            step=1,
        )
        service_level = a2.selectbox(
            "서비스수준",
            ["90%", "95%", "97%", "99%"],
            index=2,
        )
        z_values = {"90%": 1.28, "95%": 1.65, "97%": 1.88, "99%": 2.33}
        z_value = z_values[service_level]

        product_monthly = (
            filtered.groupby(group_cols + ["분석월"], dropna=False, as_index=False)["수요량"]
            .sum()
        )
        month_index = pd.period_range(
            start=pd.to_datetime(start_date).to_period("M"),
            end=pd.to_datetime(end_date).to_period("M"),
            freq="M",
        ).astype(str)
        demand_matrix = (
            product_monthly.pivot_table(
                index=group_cols,
                columns="분석월",
                values="수요량",
                aggfunc="sum",
                fill_value=0,
            )
            .reindex(columns=month_index, fill_value=0)
            .reset_index()
        )
        month_cols = list(month_index)
        demand_matrix["수요합계"] = demand_matrix[month_cols].sum(axis=1)
        demand_matrix["월평균수요"] = demand_matrix[month_cols].mean(axis=1)
        demand_matrix["월수요표준편차"] = demand_matrix[month_cols].std(axis=1, ddof=0).fillna(0)

        stock_cols = [
            col
            for col in ["제품정보코드", "현재고", "미출고수량"]
            if col in stock.columns
        ]
        optimal_stock = demand_matrix.merge(
            stock[stock_cols],
            on="제품정보코드",
            how="left",
            suffixes=("", "_현재"),
        )
        optimal_stock["현재고연결"] = optimal_stock["현재고"].notna()
        lead_time_months = lead_time_days / 30
        optimal_stock["안전재고"] = (
            z_value
            * optimal_stock["월수요표준편차"]
            * (lead_time_months ** 0.5)
        )
        optimal_stock["적정재고"] = (
            optimal_stock["월평균수요"] * lead_time_months
            + optimal_stock["안전재고"]
        )
        optimal_stock["부족수량"] = optimal_stock["적정재고"] - optimal_stock["현재고"]
        optimal_stock.loc[~optimal_stock["현재고연결"], "부족수량"] = pd.NA
        optimal_stock["권장발주량"] = optimal_stock["부족수량"].clip(lower=0).round(0)

        def judge_stock(row: pd.Series) -> str:
            current_stock = row.get("현재고", pd.NA)
            if pd.isna(current_stock):
                return "현재고 연결필요"
            if current_stock < row["안전재고"]:
                return "안전재고 미만"
            if current_stock < row["적정재고"]:
                return "발주 검토"
            return "보유 충분"

        optimal_stock["재고판정"] = optimal_stock.apply(judge_stock, axis=1)
        status_counts = optimal_stock["재고판정"].value_counts()
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("안전재고 미만", f"{int(status_counts.get('안전재고 미만', 0)):,}개")
        s2.metric("발주 검토", f"{int(status_counts.get('발주 검토', 0)):,}개")
        s3.metric("권장발주 총량", f"{optimal_stock['권장발주량'].fillna(0).sum():,.0f}")
        s4.metric("현재고 연결필요", f"{int(status_counts.get('현재고 연결필요', 0)):,}개")
        st.caption(f"분석 기준: {len(month_cols)}개월 / 리드타임 {lead_time_days}일 / 서비스수준 {service_level} / Z {z_value}")

        optimal_stock = optimal_stock.sort_values(
            ["재고판정", "권장발주량", "수요합계"],
            ascending=[True, False, False],
        )
        table_view(
            optimal_stock,
            [
                "재고판정",
                "제품정보코드",
                "제품분류",
                "제품명",
                "규격",
                "현재고",
                "수요합계",
                "월평균수요",
                "월수요표준편차",
                "안전재고",
                "적정재고",
                "부족수량",
                "권장발주량",
            ],
            height=560,
        )
        download_csv(optimal_stock, "megacell_inventory_optimal_stock_analysis.csv")
    else:
        st.info("현재고 테이블과 제품정보코드를 연결할 수 없어 현재고 대비 수요 분석은 생략했습니다.")
        download_csv(by_product, "megacell_inventory_demand_analysis.csv")
