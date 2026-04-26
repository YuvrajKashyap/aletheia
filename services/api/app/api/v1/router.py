from fastapi import APIRouter

from app.api.v1.routes import admin, datasets, health, system

router = APIRouter()
router.include_router(admin.router)
router.include_router(datasets.router)
router.include_router(health.router)
router.include_router(system.router)
