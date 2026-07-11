from __future__ import annotations

from services.db_organization_service import organize_database


def main() -> None:
    result = organize_database()
    print(f"erp_orders synced: {result.erp_order_count:,}")


if __name__ == "__main__":
    main()
