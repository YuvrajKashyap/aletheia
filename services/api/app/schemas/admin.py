from pydantic import BaseModel


class AdminStatusResponse(BaseModel):
    status: str
    app_mode: str
    admin_protection_enabled: bool
    public_mode: bool
    warnings: list[str]
    request_id: str
