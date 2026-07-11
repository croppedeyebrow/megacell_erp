from fastapi import APIRouter

router = APIRouter()


@router.get("/system/version")
def get_version() -> dict[str, str]:
    return {
        "name": "MegaCell ERP API",
        "version": "0.1.0",
        "api": "v1",
    }
