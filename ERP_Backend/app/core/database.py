from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


connect_args: dict[str, object] = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, connect_args=connect_args, future=True)

if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _sqlite_fk(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.domains.documents import models as _documents_models  # noqa: F401
    from app.domains.field import models as _field_models  # noqa: F401
    from app.domains.identity import models as _identity_models  # noqa: F401
    from app.domains.imports import models as _imports_models  # noqa: F401
    from app.domains.inventory import models as _inventory_models  # noqa: F401
    from app.domains.management import models as _management_models  # noqa: F401
    from app.domains.master_data import models as _master_data_models  # noqa: F401
    from app.domains.procurement import models as _procurement_models  # noqa: F401
    from app.domains.research import models as _research_models  # noqa: F401
    from app.domains.sales import models as _sales_models  # noqa: F401

    if settings.database_url.startswith("sqlite"):
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)
