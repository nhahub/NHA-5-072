from fastapi import APIRouter
from config.settings import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }
