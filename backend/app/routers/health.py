from fastapi import APIRouter

from app.config import Settings

router = APIRouter()


@router.get("/api/health")
async def health():
    return {"status": "healthy"}

@router.get("/api/debug/models")
async def debug_models():
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # This should be /app/app/routers
    base_app_dir = os.path.dirname(current_dir)
    # This should be /app/app/models
    models_dir = os.path.join(base_app_dir, "models")
    
    exists = os.path.exists(models_dir)
    files = os.listdir(models_dir) if exists else []
    
    return {
        "models_dir": models_dir,
        "exists": exists,
        "files": files,
        "current_file": __file__
    }
