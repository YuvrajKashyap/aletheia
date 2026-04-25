from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings = get_settings()

    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.PROJECT_VERSION,
        app_mode=settings.APP_MODE,
        request_id=request.state.request_id,
    )
