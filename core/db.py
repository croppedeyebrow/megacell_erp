from __future__ import annotations

import sqlite3

import pandas as pd
import streamlit as st

from config import DB_PATH


def quote_name(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'

def db_mtime() -> float:
    return DB_PATH.stat().st_mtime if DB_PATH.exists() else 0

def list_tables(mtime: float) -> list[str]:
    if not DB_PATH.exists():
        return []
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return [row[0] for row in rows if not row[0].startswith("sqlite_")]

def load_table(table_name: str, mtime: float) -> pd.DataFrame:
    if not DB_PATH.exists() or table_name not in list_tables(mtime):
        return pd.DataFrame()
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(f"SELECT * FROM {quote_name(table_name)}", conn)

def get_table(name: str) -> pd.DataFrame:
    return load_table(name, db_mtime())
