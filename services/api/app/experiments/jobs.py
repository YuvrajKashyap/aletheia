from __future__ import annotations

from app.db.session import SessionLocal
from app.experiments.comparison import run_evaluation_comparison


def run_evaluation_comparison_job(
    name: str,
    experiment_config_ids: list[str] | None = None,
    experiment_config_names: list[str] | None = None,
    use_defaults: bool = False,
    dataset_name: str = "beir/scifact",
    dataset_version: str = "test",
    index_version_id: str | None = None,
    query_limit: int | None = None,
    query_offset: int = 0,
    notes: str | None = None,
    rq_job_id: str | None = None,
) -> dict:
    db = SessionLocal()
    try:
        return run_evaluation_comparison(
            db,
            name=name,
            experiment_config_ids=experiment_config_ids,
            experiment_config_names=experiment_config_names,
            use_defaults=use_defaults,
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            index_version_id=index_version_id,
            query_limit=query_limit,
            query_offset=query_offset,
            notes=notes,
        )
    finally:
        db.close()
