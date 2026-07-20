# Inventory Domain

Owns stock status, stock movements, inventory adjustments, and battery inventory.

## Responsibilities

- Current stock lookup for products, materials, and batteries
- Inbound/outbound movement records
- Inventory movement and adjustment history
- Demand analysis and inventory reference data

## File Roles

- `models.py`: SQLAlchemy ORM models for this domain.
- `schemas.py`: Pydantic request/response schemas for API contracts.
- `api.py`: FastAPI router and HTTP boundary for this domain.
- `service.py`: Use-case orchestration and domain business rules.
- `repository.py`: Database query and persistence helpers.

## Development Notes

- Keep HTTP-specific code in `api.py`.
- Keep DB queries in `repository.py`.
- Keep business decisions in `service.py`.
- Shared master data should be referenced from `master_data` instead of being duplicated.
