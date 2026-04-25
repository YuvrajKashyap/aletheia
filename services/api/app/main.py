from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.middleware import request_id_middleware, request_logging_middleware

settings = get_settings()

configure_logging()

app = FastAPI(
    title="Aletheia API",
    version=settings.PROJECT_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.middleware("http")(request_logging_middleware)
app.middleware("http")(request_id_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "aletheia-api",
        "status": "ok",
        "docs": "/api/docs",
    }
