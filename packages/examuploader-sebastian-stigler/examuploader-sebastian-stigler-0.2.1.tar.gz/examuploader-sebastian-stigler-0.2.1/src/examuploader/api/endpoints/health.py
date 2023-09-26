from fastapi import APIRouter, Request

from examuploader.models.health_check import HealthCheck

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheck)
async def health_check(request: Request):
    """Health Check endpoint"""

    return HealthCheck(
        message=request.app.title,
        version=request.app.version,
        docs_url=request.app.docs_url,
        redoc_url=request.app.redoc_url,
    )

