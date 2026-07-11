from __future__ import annotations

ALL_PERMISSIONS: list[str] = [
    "home.view",
    "sales.view",
    "sales.edit",
    "production.view",
    "production.edit",
    "purchasing.view",
    "inventory.view",
    "inventory.adjust",
    "as.view",
    "as.edit",
    "master.view",
    "analytics.view",
    "admin.view",
    "admin.manage",
    "document.generate",
    "report.export",
]

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": list(ALL_PERMISSIONS),
    "executive": [
        "home.view",
        "sales.view",
        "production.view",
        "purchasing.view",
        "inventory.view",
        "as.view",
        "analytics.view",
        "report.export",
    ],
    "manager": [
        "home.view",
        "sales.view",
        "sales.edit",
        "production.view",
        "production.edit",
        "purchasing.view",
        "inventory.view",
        "inventory.adjust",
        "as.view",
        "as.edit",
        "master.view",
        "analytics.view",
        "document.generate",
        "report.export",
    ],
    "staff": [
        "home.view",
        "sales.view",
        "sales.edit",
        "production.view",
        "purchasing.view",
        "inventory.view",
        "as.view",
        "as.edit",
        "master.view",
        "document.generate",
    ],
    "viewer": [
        "home.view",
        "sales.view",
        "production.view",
        "purchasing.view",
        "inventory.view",
        "as.view",
        "analytics.view",
    ],
}


def permissions_for_role(role: str) -> list[str]:
    return list(ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["viewer"]))
