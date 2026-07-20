# Sales Domain

Owns technical-sales workflows from customer contact to delivery progress.

## Responsibilities

- Customer and account sales management
- Sales leads and activity history
- Quotation and sales order management
- Quote/order document conversion
- Delivery schedule and sales progress tracking

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
