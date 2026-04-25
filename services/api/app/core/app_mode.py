ALLOWED_APP_MODES = {"local", "demo", "production"}
PUBLIC_APP_MODES = {"demo", "production"}
DEFAULT_ADMIN_API_KEY = "replace-me"


def normalize_app_mode(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized in ALLOWED_APP_MODES:
        return normalized
    return "local"


def is_public_app_mode(app_mode: str) -> bool:
    return normalize_app_mode(app_mode) in PUBLIC_APP_MODES


def validate_admin_key_for_mode(app_mode: str, admin_api_key: str) -> list[str]:
    warnings: list[str] = []
    normalized_mode = normalize_app_mode(app_mode)
    normalized_key = (admin_api_key or "").strip()

    if normalized_mode in PUBLIC_APP_MODES and not normalized_key:
        warnings.append("ADMIN_API_KEY must be set in demo or production mode.")

    if normalized_mode in PUBLIC_APP_MODES and normalized_key == DEFAULT_ADMIN_API_KEY:
        warnings.append("ADMIN_API_KEY must not use the default value in demo or production mode.")

    return warnings
