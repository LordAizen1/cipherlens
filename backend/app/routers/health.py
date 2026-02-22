from fastapi import APIRouter

from app.config import Settings

router = APIRouter()


@router.get("/api/health")
async def health():
    settings = Settings()
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "mock_mode": settings.USE_MOCK_MODEL,
    }
