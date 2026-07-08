from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path
from typing import Iterable

import pandas as pd

from config import ADMIN_EMAILS, BASE_DIR, BATTERY_EXPORT_DIR, DATA_DIR, DB_PATH, ensure_runtime_dirs


def find_file(pattern: str) -> Path:
    search_dirs = [DATA_DIR, BASE_DIR]
    for directory in search_dirs:
        matches = sorted(directory.glob(pattern))
        if matches:
            return matches[0]
    searched = ", ".join(str(path) for path in search_dirs)
    raise FileNotFoundError(f"파일을 찾을 수 없습니다: {pattern} (검색 위치: {searched})")


def unique_columns(columns: Iterable[object]) -> list[str]:
    seen: dict[str, int] = {}
    result: list[str] = []
    for value in columns:
        name = "" if pd.isna(value) else str(value).strip()
        if not name or name.startswith("Unnamed"):
            name = "컬럼"
        count = seen.get(name, 0)
        seen[name] = count + 1
        result.append(name if count == 0 else f"{name}.{count}")
    return result


def tidy_frame(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = unique_columns(df.columns)
    df = df.dropna(how="all")
    df = df.loc[:, [not str(col).startswith("컬럼.") for col in df.columns]]
    return df.reset_index(drop=True)


def drop_duplicate_helper_columns(df: pd.DataFrame) -> pd.DataFrame:
    keep = [
        col
        for col in df.columns
        if not str(col).startswith("Unnamed") and not str(col).endswith(".1")
    ]
    return df[keep].copy()


def write_table(conn: sqlite3.Connection, name: str, df: pd.DataFrame) -> None:
    df = tidy_frame(df)
    df.to_sql(name, conn, if_exists="replace", index=False)
    print(f"{name}: {len(df):,}건")


def clean_csv_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df = tidy_frame(df)
    df = df.replace("", pd.NA).dropna(how="all").fillna("")
    return df.reset_index(drop=True)


def parse_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).str.strip(),
        errors="coerce",
    ).fillna(0)


def import_orders(conn: sqlite3.Connection) -> None:
    path = find_file("영업_2026년 수주관리대장.xlsx")
    df = pd.read_excel(path, sheet_name="2026년수주", header=3, engine="openpyxl")
    df = tidy_frame(df)
    rename = {
        "품명 및 규격": "품명규격",
        "V.A.T 포함": "vat포함",
    }
    df = df.rename(columns=rename)
    cols = [
        "월",
        "구분",
        "수주일자",
        "제조지시서",
        "납품처",
        "품명규격",
        "단위",
        "수량",
        "단가",
        "수주금액",
        "vat포함",
        "발주처",
        "발주처담당",
        "출고요청일",
        "출고일",
        "계산서",
        "비고",
    ]
    df = df[[col for col in cols if col in df.columns]]
    df = df[df.get("수주일자", pd.Series(dtype=object)).notna()]
    write_table(conn, "수주", df)


def import_inventory(conn: sqlite3.Connection) -> None:
    path = find_file("(주)메가셀_간편재고관리프로그램.xlsm")
    product = pd.read_excel(path, sheet_name="제품정보", header=0, engine="openpyxl")
    product = drop_duplicate_helper_columns(tidy_frame(product))
    product_cols = [
        "제품정보코드",
        "제품분류",
        "제품명",
        "유형",
        "통신카드",
        "규격",
        "입고수량",
        "미출고수량",
        "출고수량",
        "현재고",
        "비고",
    ]
    product = product[[col for col in product_cols if col in product.columns]]
    if "제품정보코드" in product.columns:
        product = product[product["제품정보코드"].notna()]
    write_table(conn, "재고", product)

    history = pd.read_excel(path, sheet_name="재고정보", header=0, engine="openpyxl")
    history = drop_duplicate_helper_columns(tidy_frame(history))
    history_cols = [
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
    ]
    history = history[[col for col in history_cols if col in history.columns]]
    if "재고정보코드" in history.columns:
        history = history[history["재고정보코드"].notna()]
    write_table(conn, "재고출납", history)


def import_as(conn: sqlite3.Connection) -> None:
    path = find_file("AS관리대장_자동화버전*.xlsm")
    df = pd.read_excel(path, sheet_name="관리내역", header=2, engine="openpyxl")
    df = tidy_frame(df)
    df = df.rename(
        columns={
            "제품명/장비명": "제품명",
            "S/N": "SN",
            "유무상구분": "유무상",
            "수리담당자": "담당자",
        }
    )
    write_table(conn, "AS관리", df)


def import_materials(conn: sqlite3.Connection) -> None:
    path = find_file("자재리스트 관리 양식__v0.8.xlsm")
    parts = pd.read_excel(path, sheet_name="부품리스트", header=6, engine="openpyxl")
    stock = pd.read_excel(path, sheet_name="재고현황", header=9, engine="openpyxl")
    bom = pd.read_excel(path, sheet_name="BOM 관리", header=6, engine="openpyxl")

    write_table(conn, "부품리스트", tidy_frame(parts))
    write_table(conn, "자재재고", drop_duplicate_helper_columns(tidy_frame(stock)))
    write_table(conn, "BOM", tidy_frame(bom).rename(columns={"Q'ty": "소요량"}))


def import_purchases(conn: sqlite3.Connection) -> None:
    path = find_file("자재발주현황_발주서 통합 양식.xlsm")
    df = pd.read_excel(path, sheet_name="발주현황", header=4, engine="openpyxl")
    write_table(conn, "발주현황", tidy_frame(df))


def import_battery(conn: sqlite3.Connection) -> None:
    path = find_file("배터리관리v1.04_QR수정버전.xlsb")
    try:
        xls = pd.ExcelFile(path, engine="pyxlsb")
    except ImportError:
        xls = None
    except Exception as exc:
        print(f"배터리: pyxlsb 읽기 실패, Excel COM 방식으로 재시도({exc})")
        xls = None

    if xls is None:
        export_dir = BATTERY_EXPORT_DIR
        script = BASE_DIR / "export_battery_xlsb.ps1"
        if not script.exists():
            pd.DataFrame(columns=["안내"]).to_sql("배터리재고", conn, if_exists="replace", index=False)
            print("배터리: export_battery_xlsb.ps1 없음")
            return

        command = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-WorkbookPath",
            str(path),
            "-OutputDir",
            str(export_dir),
        ]
        subprocess.run(command, check=True)

        stock = clean_csv_table(export_dir / "battery_stock.csv")
        transactions = clean_csv_table(export_dir / "battery_transactions.csv")
        items = clean_csv_table(export_dir / "battery_items.csv")
        schedule = clean_csv_table(export_dir / "battery_schedule.csv")
        usage_log = clean_csv_table(export_dir / "battery_usage_log.csv")

        if "품목명" in stock.columns:
            stock = stock[stock["품목명"].astype(str).str.strip() != ""]
            stock = stock[stock["품목명"].astype(str).str.strip() != "품목명"]
        for col in ["입고", "출고", "미출고", "재고"]:
            if col in stock.columns:
                stock[col] = parse_number(stock[col])

        if "ID" in transactions.columns:
            transactions = transactions[transactions["ID"].astype(str).str.strip() != ""]
        for col in ["단가", "수량", "금액"]:
            if col in transactions.columns:
                transactions[col] = parse_number(transactions[col])

        if "품목코드" in items.columns:
            items = items[items["품목코드"].astype(str).str.strip() != ""]
        if "단가" in items.columns:
            items["단가"] = parse_number(items["단가"])

        if "품목명" in schedule.columns:
            schedule = schedule[schedule["품목명"].astype(str).str.strip() != ""]
        for col in schedule.columns:
            if col != "품목명":
                schedule[col] = parse_number(schedule[col])

        if "일시" in usage_log.columns:
            usage_log = usage_log[usage_log["일시"].astype(str).str.strip() != ""]

        stock.to_sql("배터리재고", conn, if_exists="replace", index=False)
        transactions.to_sql("배터리입출고", conn, if_exists="replace", index=False)
        items.to_sql("배터리품목", conn, if_exists="replace", index=False)
        schedule.to_sql("배터리출고일정", conn, if_exists="replace", index=False)
        usage_log.to_sql("배터리사용이력", conn, if_exists="replace", index=False)
        pd.DataFrame({"테이블": ["배터리재고", "배터리입출고", "배터리품목", "배터리출고일정", "배터리사용이력"]}).to_sql(
            "배터리", conn, if_exists="replace", index=False
        )
        print(
            "배터리: "
            f"재고 {len(stock):,}건, "
            f"입출고 {len(transactions):,}건, "
            f"품목 {len(items):,}건, "
            f"출고일정 {len(schedule):,}건, "
            f"사용이력 {len(usage_log):,}건"
        )
        return

    frames: list[pd.DataFrame] = []
    for sheet_name in xls.sheet_names:
        try:
            sheet_df = pd.read_excel(xls, sheet_name=sheet_name, header=0)
        except Exception:
            continue
        sheet_df = tidy_frame(sheet_df)
        if sheet_df.empty:
            continue
        sheet_df.insert(0, "시트", sheet_name)
        frames.append(sheet_df)

    df = pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()
    write_table(conn, "배터리", df)



def fetch_existing_users() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            exists = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            ).fetchone()
            if not exists:
                return pd.DataFrame()
            return pd.read_sql("SELECT * FROM users", conn)
    except Exception:
        return pd.DataFrame()


def ensure_users_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL DEFAULT '',
            department TEXT NOT NULL DEFAULT '',
            role TEXT NOT NULL DEFAULT '일반사용자',
            can_create_documents INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 0,
            password_hash TEXT,
            password_salt TEXT,
            password_iterations INTEGER NOT NULL DEFAULT 240000,
            must_change_password INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_login_at TEXT
        )
        """
    )
    existing = {row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
    migrations = {
        "password_hash": "ALTER TABLE users ADD COLUMN password_hash TEXT",
        "password_salt": "ALTER TABLE users ADD COLUMN password_salt TEXT",
        "password_iterations": "ALTER TABLE users ADD COLUMN password_iterations INTEGER NOT NULL DEFAULT 240000",
        "must_change_password": "ALTER TABLE users ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0",
    }
    for column, sql in migrations.items():
        if column not in existing:
            conn.execute(sql)

def seed_admin_users(conn: sqlite3.Connection) -> None:
    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    for email in sorted(ADMIN_EMAILS):
        conn.execute(
            """
            INSERT INTO users (
                email, name, department, role, can_create_documents,
                is_active, created_at, updated_at
            )
            VALUES (?, ?, '경영지원팀', '관리자', 1, 1, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                role='관리자',
                can_create_documents=1,
                is_active=1,
                updated_at=excluded.updated_at
            """,
            (email, email.split("@")[0], timestamp, timestamp),
        )


def restore_users(conn: sqlite3.Connection, users: pd.DataFrame) -> None:
    ensure_users_schema(conn)
    if not users.empty:
        users.to_sql("users", conn, if_exists="replace", index=False)
        ensure_users_schema(conn)
        print(f"users: {len(users):,}명 복원")
    seed_admin_users(conn)

def main() -> None:
    ensure_runtime_dirs()
    existing_users = fetch_existing_users()
    if DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as conn:
        import_orders(conn)
        import_inventory(conn)
        import_as(conn)
        import_materials(conn)
        import_purchases(conn)
        import_battery(conn)
        restore_users(conn, existing_users)

    print(f"\n완료: {DB_PATH}")


if __name__ == "__main__":
    main()
