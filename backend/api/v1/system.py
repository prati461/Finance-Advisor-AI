from fastapi import APIRouter

from backend.core.config import settings

router = APIRouter(prefix="", tags=["system"])


@router.get("/health", summary="Health check")
def health() -> dict:
    return {"status": "ok"}


@router.get("/version", summary="API version")
def version() -> dict:
    return {"version": settings.version, "name": settings.app_name}
