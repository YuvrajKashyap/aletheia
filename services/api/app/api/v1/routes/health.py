from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db import health as db_health
from app.schemas.health import DatabaseHealthResponse, HealthResponse

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


@router.get("/health/db", response_model=DatabaseHealthResponse)
async def database_health(request: Request) -> JSONResponse:
    result = db_health.check_database_health()

    response = DatabaseHealthResponse(
        status=result["status"] or "unhealthy",
        database=result["database"] or "postgresql",
        error=result["error"],
        request_id=request.state.request_id,
    )

    status_code = (
        status.HTTP_200_OK
        if response.status == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
    )
