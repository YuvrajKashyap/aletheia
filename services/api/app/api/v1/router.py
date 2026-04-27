from fastapi import APIRouter

from app.api.v1.routes import (
    admin,
    datasets,
    evaluations,
    experiments,
    health,
    indexes,
    ingestion,
    search,
    system,
)

router = APIRouter()
router.include_router(admin.router)
router.include_router(datasets.router)
router.include_router(evaluations.router)
router.include_router(experiments.router)
router.include_router(health.router)
router.include_router(indexes.router)
router.include_router(ingestion.router)
router.include_router(search.router)
router.include_router(system.router)
