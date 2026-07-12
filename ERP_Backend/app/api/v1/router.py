from fastapi import APIRouter

from app.api.v1 import system
from app.domains.identity.api import router as auth_router
from app.domains.sales.api import router as sales_router

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(auth_router)
api_router.include_router(sales_router)
