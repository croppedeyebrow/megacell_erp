# Imports Domain

Owns Excel source loading, column mapping, import logs, and source traceability.

## Responsibilities

- Register Excel files and analyze sheets/columns
- Load original row data
- Apply imported data to ERP operation tables
- Track import success and failure logs
- Protect ERP-edited data from source reload overwrites

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
