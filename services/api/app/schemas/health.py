from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    app_mode: str
    request_id: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str
    request_id: str
    error: str | None = None
