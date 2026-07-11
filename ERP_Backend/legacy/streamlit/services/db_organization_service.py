from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from config import DB_PATH
from repositories.erp_schema_repository import ensure_erp_schema, sync_erp_orders_from_source
from repositories.user_repository import ensure_users_schema, seed_admin_users


@dataclass(frozen=True)
class DbOrganizationResult:
    erp_order_count: int


def organize_database() -> DbOrganizationResult:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        ensure_users_schema(conn)
        seed_admin_users(conn)
        ensure_erp_schema(conn)
        erp_order_count = sync_erp_orders_from_source(conn)
        conn.commit()
    return DbOrganizationResult(erp_order_count=erp_order_count)
