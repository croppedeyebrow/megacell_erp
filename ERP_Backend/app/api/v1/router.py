from fastapi import APIRouter

from app.api.v1 import system
from app.domains.documents.api import router as documents_router
from app.domains.field.api import router as field_router
from app.domains.identity.api import router as auth_router
from app.domains.imports.api import router as imports_router
from app.domains.inventory.api import router as inventory_router
from app.domains.management.api import router as management_router
from app.domains.master_data.api import router as master_data_router
from app.domains.research.api import router as research_router
from app.domains.sales.api import router as sales_router

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(auth_router)
api_router.include_router(master_data_router)
api_router.include_router(management_router)
api_router.include_router(sales_router)
api_router.include_router(research_router)
api_router.include_router(field_router)
api_router.include_router(inventory_router)
api_router.include_router(documents_router)
api_router.include_router(imports_router)
