from __future__ import annotations

from typing import Iterable

import pandas as pd
import streamlit as st

from core.db import get_table


def normalize_numeric(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("원", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce").fillna(0)

def prepare_numeric(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = normalize_numeric(df[col])
    return df

def clean_display(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    keep = [
        col
        for col in df.columns
        if not str(col).startswith("Unnamed") and not str(col).startswith("컬럼")
    ]
    return df[keep].dropna(how="all").reset_index(drop=True)

def text_filter(
    df: pd.DataFrame,
    keyword: str,
    columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    if df.empty or not keyword:
        return df
    target_cols = [col for col in (columns or df.columns) if col in df.columns]
    if not target_cols:
        target_cols = list(df.columns)
    mask = (
        df[target_cols]
        .astype(str)
        .apply(lambda col: col.str.contains(keyword, case=False, na=False))
        .any(axis=1)
    )
    return df[mask]

def safe_unique(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df.columns:
        return []
    values = df[column].dropna().astype(str).str.strip()
    return sorted(value for value in values.unique() if value and value != "nan")

def table_view(
    df: pd.DataFrame,
    preferred_cols: Iterable[str] | None = None,
    height: int = 560,
) -> None:
    df = clean_display(df)
    cols = [col for col in (preferred_cols or df.columns) if col in df.columns]
    if not cols:
        cols = list(df.columns)
    st.dataframe(df[cols], width="stretch", height=height, hide_index=True)

def download_csv(df: pd.DataFrame, filename: str) -> None:
    st.download_button(
        "CSV 내려받기",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=filename,
        mime="text/csv",
        width="stretch",
    )

def metric_sum(df: pd.DataFrame, column: str, suffix: str = "") -> str:
    if column not in df.columns:
        return "-"
    return f"{normalize_numeric(df[column]).sum():,.0f}{suffix}"

def searchable_table(
    table_name: str,
    title: str,
    search_label: str,
    search_cols: Iterable[str] | None,
    preferred_cols: Iterable[str] | None = None,
    csv_name: str | None = None,
) -> pd.DataFrame:
    st.subheader(title)
    df = clean_display(get_table(table_name))
    keyword = st.text_input(search_label, key=f"search_{table_name}_{title}")
    filtered = text_filter(df, keyword, search_cols)
    st.metric("검색 결과", f"{len(filtered):,}건")
    table_view(filtered, preferred_cols)
    if csv_name:
        download_csv(filtered, csv_name)
    return filtered
