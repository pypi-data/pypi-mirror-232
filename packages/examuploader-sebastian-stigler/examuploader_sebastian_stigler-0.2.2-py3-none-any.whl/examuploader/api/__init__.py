from fastapi import APIRouter
from examuploader.api.endpoints import health, upload

router = APIRouter(prefix="/api")

router.include_router(health.router)
router.include_router(upload.router)