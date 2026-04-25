from fastapi import APIRouter, Depends, Request

from app.api.dependencies.admin import AdminContext, require_admin
from app.core.config import Settings, get_settings
from app.schemas.admin import AdminStatusResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/status", response_model=AdminStatusResponse)
async def admin_status(
    request: Request,
    admin_context: AdminContext = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> AdminStatusResponse:
    return AdminStatusResponse(
        status="ok",
        app_mode=admin_context.app_mode,
        admin_protection_enabled=admin_context.authenticated,
        public_mode=settings.public_app_mode,
        warnings=settings.admin_key_warnings,
        request_id=request.state.request_id,
    )
