# Field Engineering Domain

Owns field-engineering workflows for installation, service, visits, inspections, and reports.

## Responsibilities

- Installation schedule management
- Work order management
- Site visit records
- AS/service case handling
- Battery inspections
- Field photos and attachments
- Field reports

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
