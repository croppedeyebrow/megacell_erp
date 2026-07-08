from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any


ORDER_SOURCE_TABLE = "수주"


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    return (
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        ).fetchone()
        is not None
    )


def quote_name(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    return {str(row[1]) for row in conn.execute(f"PRAGMA table_info({quote_name(table_name)})")}


def ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    if column_name not in table_columns(conn, table_name):
        conn.execute(f"ALTER TABLE {quote_name(table_name)} ADD COLUMN {column_name} {definition}")


def ensure_erp_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS erp_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_table TEXT NOT NULL,
            source_key TEXT NOT NULL UNIQUE,
            source_row_id TEXT,
            manufacturing_order_no TEXT,
            order_date TEXT,
            category TEXT,
            customer_name TEXT,
            vendor_name TEXT,
            product_name TEXT,
            unit TEXT,
            quantity REAL,
            unit_price REAL,
            order_amount REAL,
            vat_amount REAL,
            invoice_status TEXT,
            shipment_request_date TEXT,
            shipped_date TEXT,
            shipment_status TEXT NOT NULL DEFAULT '미출고',
            memo TEXT,
            erp_modified INTEGER NOT NULL DEFAULT 0,
            source_payload_json TEXT,
            source_synced_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            updated_by TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS erp_order_change_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            changed_by TEXT,
            changed_at TEXT NOT NULL,
            reason TEXT,
            FOREIGN KEY(order_id) REFERENCES erp_orders(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS erp_inventory_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movement_date TEXT NOT NULL,
            item_code TEXT,
            item_name TEXT,
            movement_type TEXT NOT NULL,
            quantity REAL NOT NULL DEFAULT 0,
            reference_type TEXT,
            reference_id TEXT,
            memo TEXT,
            created_by TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS erp_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_type TEXT NOT NULL,
            reference_type TEXT,
            reference_id TEXT,
            file_name TEXT,
            file_path TEXT,
            created_by TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS erp_sync_state (
            sync_key TEXT PRIMARY KEY,
            synced_at TEXT NOT NULL,
            row_count INTEGER NOT NULL DEFAULT 0,
            memo TEXT
        )
        """
    )

    ensure_column(conn, "erp_orders", "erp_modified", "INTEGER NOT NULL DEFAULT 0")
    ensure_column(conn, "erp_orders", "source_synced_at", "TEXT")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_erp_orders_status ON erp_orders(shipment_status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_erp_orders_order_date ON erp_orders(order_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_erp_orders_customer ON erp_orders(customer_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_erp_order_logs_order_id ON erp_order_change_logs(order_id)")


def normalize_value(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text in {"nan", "NaN", "None", "NaT"}:
        return ""
    return text


def parse_number(value: Any) -> float | None:
    text = normalize_value(value).replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def get_value(row: sqlite3.Row, key: str) -> Any:
    return row[key] if key in row.keys() else None


def build_order_record(row: sqlite3.Row) -> dict[str, Any]:
    source_row_id = str(row["rowid"])
    manufacturing_order_no = normalize_value(get_value(row, "제조지시서"))
    if not manufacturing_order_no:
        manufacturing_order_no = f"row-{source_row_id}"

    shipped_date = normalize_value(get_value(row, "출고일"))
    shipment_status = "출고완료" if shipped_date else "미출고"
    payload = {key: row[key] for key in row.keys() if key != "rowid"}

    return {
        "source_table": ORDER_SOURCE_TABLE,
        "source_key": f"{ORDER_SOURCE_TABLE}:{manufacturing_order_no}:{source_row_id}",
        "source_row_id": source_row_id,
        "manufacturing_order_no": manufacturing_order_no,
        "order_date": normalize_value(get_value(row, "수주일자")),
        "category": normalize_value(get_value(row, "구분")),
        "customer_name": normalize_value(get_value(row, "납품처")),
        "vendor_name": normalize_value(get_value(row, "발주처")),
        "product_name": normalize_value(get_value(row, "품명규격")),
        "unit": normalize_value(get_value(row, "단위")),
        "quantity": parse_number(get_value(row, "수량")),
        "unit_price": parse_number(get_value(row, "단가")),
        "order_amount": parse_number(get_value(row, "수주금액")),
        "vat_amount": parse_number(get_value(row, "vat포함")),
        "invoice_status": normalize_value(get_value(row, "계산서")),
        "shipment_request_date": normalize_value(get_value(row, "출고요청일")),
        "shipped_date": shipped_date,
        "shipment_status": shipment_status,
        "memo": normalize_value(get_value(row, "비고")),
        "source_payload_json": json.dumps(payload, ensure_ascii=False, default=str),
    }


def sync_erp_orders_from_source(conn: sqlite3.Connection) -> int:
    ensure_erp_schema(conn)
    if not table_exists(conn, ORDER_SOURCE_TABLE):
        return 0

    conn.row_factory = sqlite3.Row
    timestamp = now_text()
    rows = conn.execute(f"SELECT rowid, * FROM {quote_name(ORDER_SOURCE_TABLE)}").fetchall()
    count = 0
    for row in rows:
        record = build_order_record(row)
        conn.execute(
            """
            INSERT INTO erp_orders (
                source_table, source_key, source_row_id, manufacturing_order_no,
                order_date, category, customer_name, vendor_name, product_name,
                unit, quantity, unit_price, order_amount, vat_amount, invoice_status,
                shipment_request_date, shipped_date, shipment_status, memo,
                source_payload_json, source_synced_at, created_at, updated_at
            )
            VALUES (
                :source_table, :source_key, :source_row_id, :manufacturing_order_no,
                :order_date, :category, :customer_name, :vendor_name, :product_name,
                :unit, :quantity, :unit_price, :order_amount, :vat_amount, :invoice_status,
                :shipment_request_date, :shipped_date, :shipment_status, :memo,
                :source_payload_json, :timestamp, :timestamp, :timestamp
            )
            ON CONFLICT(source_key) DO UPDATE SET
                source_row_id=excluded.source_row_id,
                source_payload_json=excluded.source_payload_json,
                source_synced_at=excluded.source_synced_at,
                manufacturing_order_no=CASE WHEN erp_orders.erp_modified=0 THEN excluded.manufacturing_order_no ELSE erp_orders.manufacturing_order_no END,
                order_date=CASE WHEN erp_orders.erp_modified=0 THEN excluded.order_date ELSE erp_orders.order_date END,
                category=CASE WHEN erp_orders.erp_modified=0 THEN excluded.category ELSE erp_orders.category END,
                customer_name=CASE WHEN erp_orders.erp_modified=0 THEN excluded.customer_name ELSE erp_orders.customer_name END,
                vendor_name=CASE WHEN erp_orders.erp_modified=0 THEN excluded.vendor_name ELSE erp_orders.vendor_name END,
                product_name=CASE WHEN erp_orders.erp_modified=0 THEN excluded.product_name ELSE erp_orders.product_name END,
                unit=CASE WHEN erp_orders.erp_modified=0 THEN excluded.unit ELSE erp_orders.unit END,
                quantity=CASE WHEN erp_orders.erp_modified=0 THEN excluded.quantity ELSE erp_orders.quantity END,
                unit_price=CASE WHEN erp_orders.erp_modified=0 THEN excluded.unit_price ELSE erp_orders.unit_price END,
                order_amount=CASE WHEN erp_orders.erp_modified=0 THEN excluded.order_amount ELSE erp_orders.order_amount END,
                vat_amount=CASE WHEN erp_orders.erp_modified=0 THEN excluded.vat_amount ELSE erp_orders.vat_amount END,
                invoice_status=CASE WHEN erp_orders.erp_modified=0 THEN excluded.invoice_status ELSE erp_orders.invoice_status END,
                shipment_request_date=CASE WHEN erp_orders.erp_modified=0 THEN excluded.shipment_request_date ELSE erp_orders.shipment_request_date END,
                shipped_date=CASE WHEN erp_orders.erp_modified=0 THEN excluded.shipped_date ELSE erp_orders.shipped_date END,
                shipment_status=CASE WHEN erp_orders.erp_modified=0 THEN excluded.shipment_status ELSE erp_orders.shipment_status END,
                memo=CASE WHEN erp_orders.erp_modified=0 THEN excluded.memo ELSE erp_orders.memo END,
                updated_at=CASE WHEN erp_orders.erp_modified=0 THEN excluded.updated_at ELSE erp_orders.updated_at END
            """,
            {**record, "timestamp": timestamp},
        )
        count += 1

    conn.execute(
        """
        INSERT INTO erp_sync_state(sync_key, synced_at, row_count, memo)
        VALUES('erp_orders_from_source', ?, ?, '수주 원본에서 erp_orders 동기화')
        ON CONFLICT(sync_key) DO UPDATE SET
            synced_at=excluded.synced_at,
            row_count=excluded.row_count,
            memo=excluded.memo
        """,
        (timestamp, count),
    )
    return count


def record_order_change(
    conn: sqlite3.Connection,
    *,
    order_id: int,
    field_name: str,
    old_value: Any,
    new_value: Any,
    changed_by: str,
    reason: str = "",
) -> None:
    timestamp = now_text()
    conn.execute(
        """
        INSERT INTO erp_order_change_logs(
            order_id, field_name, old_value, new_value, changed_by, changed_at, reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            order_id,
            field_name,
            normalize_value(old_value),
            normalize_value(new_value),
            changed_by,
            timestamp,
            reason,
        ),
    )
    conn.execute(
        "UPDATE erp_orders SET erp_modified=1, updated_at=?, updated_by=? WHERE id=?",
        (timestamp, changed_by, order_id),
    )
