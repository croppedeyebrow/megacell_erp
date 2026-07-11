from __future__ import annotations

import calendar
from datetime import date

import pandas as pd
import streamlit as st

from core.ui import clean_display


def build_current_inventory(history: pd.DataFrame) -> pd.DataFrame:
    history = prepare_numeric(
        clean_display(history),
        ["입고수량", "미출고수량", "출고수량", "잔고수량"],
    )
    if history.empty:
        return history

    key_cols = [
        col
        for col in ["제품분류", "제품명", "유형", "통신카드", "규격"]
        if col in history.columns
    ]
    if not key_cols:
        return history

    numeric_cols = [
        col
        for col in ["입고수량", "미출고수량", "출고수량", "잔고수량"]
        if col in history.columns
    ]
    work = history.copy()
    work[key_cols] = work[key_cols].fillna("")

    current = work.groupby(key_cols, dropna=False)[numeric_cols].sum().reset_index()
    if "잔고수량" not in current.columns and {"입고수량", "출고수량"}.issubset(current.columns):
        current["잔고수량"] = current["입고수량"] - current["출고수량"]

    latest_cols = [col for col in ["일자", "세부내역"] if col in work.columns]
    if latest_cols:
        latest = work.copy()
        latest["_정렬일자"] = pd.to_datetime(latest.get("일자"), errors="coerce")
        latest = latest.sort_values("_정렬일자").groupby(key_cols, dropna=False).tail(1)
        latest = latest[key_cols + latest_cols].rename(
            columns={"일자": "최종일자", "세부내역": "최근세부내역"}
        )
        current = current.merge(latest, on=key_cols, how="left")

    sort_cols = [col for col in ["제품분류", "제품명", "규격"] if col in current.columns]
    if sort_cols:
        current = current.sort_values(sort_cols)
    return current.reset_index(drop=True)

def parse_schedule_date(value: object) -> date | None:
    text = "" if pd.isna(value) else str(value).strip()
    if not text:
        return None

    direct = pd.to_datetime(text, errors="coerce")
    if pd.notna(direct):
        return direct.date()

    match = re.search(r"(20\d{2})[.\-/년\s]+(\d{1,2})(?:[.\-/월\s]+(\d{1,2}))?", text)
    if not match:
        return None

    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3) or 1)
    try:
        return date(year, month, day)
    except ValueError:
        return None

def build_pending_battery(transactions: pd.DataFrame) -> pd.DataFrame:
    transactions = prepare_numeric(transactions, ["단가", "수량", "금액"])
    if transactions.empty or "구분" not in transactions.columns:
        return transactions

    pending = transactions[
        transactions["구분"].astype(str).str.contains("미출고", na=False)
    ].copy()
    if pending.empty:
        return pending

    pending["달력일자"] = pending["출고일자"].apply(parse_schedule_date)
    pending["년월"] = pending["달력일자"].apply(lambda x: x.strftime("%Y-%m") if x else "")
    return pending.reset_index(drop=True)

def render_pending_calendar(pending: pd.DataFrame, month_key: str) -> None:
    if pending.empty or not month_key:
        st.info("달력에 표시할 미출고 일정이 없습니다.")
        return

    year, month = [int(part) for part in month_key.split("-")]
    calendar.setfirstweekday(calendar.SUNDAY)

    headers = ["일", "월", "화", "수", "목", "금", "토"]
    for col, label in zip(st.columns(7), headers):
        col.markdown(f"**{label}**")

    scheduled = pending[pending["년월"] == month_key].copy()
    by_day = {day: group for day, group in scheduled.groupby(scheduled["달력일자"].apply(lambda x: x.day))}

    for week in calendar.monthcalendar(year, month):
        cols = st.columns(7)
        for col, day_num in zip(cols, week):
            with col.container(border=True):
                if day_num == 0:
                    st.caption(" ")
                    st.write("")
                    continue
                st.caption(f"{day_num}일")
                day_rows = by_day.get(day_num)
                if day_rows is None or day_rows.empty:
                    st.write("")
                    continue
                for _, row in day_rows.iterrows():
                    qty = normalize_numeric(pd.Series([row.get("수량", 0)])).iloc[0]
                    label = f"{row.get('품목명', '')} / {qty:,.0f}개"
                    memo = str(row.get("메모", "")).strip()
                    order_no = str(row.get("주문서 번호", "")).strip()
                    st.markdown(f"**{label}**")
                    if memo:
                        st.caption(memo)
                    if order_no:
                        st.caption(order_no)
