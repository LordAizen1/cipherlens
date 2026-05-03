from fastapi import APIRouter

from app.config import Settings

router = APIRouter()


@router.get("/api/health")
async def health():
    return {"status": "healthy"}
