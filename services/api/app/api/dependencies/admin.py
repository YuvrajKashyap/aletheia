from dataclasses import dataclass
import hmac

from fastapi import Depends, HTTPException, Request, status

from app.core.app_mode import normalize_app_mode
from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class AdminContext:
    app_mode: str
    authenticated: bool


def _extract_admin_key(request: Request) -> str | None:
    header_key = request.headers.get("X-Admin-API-Key")
    if header_key:
        return header_key

    authorization = request.headers.get("Authorization")
    if not authorization:
        return None

    scheme, separator, token = authorization.partition(" ")
    if separator and scheme.lower() == "bearer" and token:
        return token

    return None


def require_admin(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> AdminContext:
    app_mode = normalize_app_mode(settings.APP_MODE)
    configured_key = (settings.ADMIN_API_KEY or "").strip()

    if settings.admin_key_warnings:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unsafe admin API key configuration for current app mode.",
        )

    provided_key = _extract_admin_key(request)
    if not provided_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin API key is required.",
        )

    if not configured_key or not hmac.compare_digest(provided_key, configured_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key.",
        )

    return AdminContext(app_mode=app_mode, authenticated=True)
