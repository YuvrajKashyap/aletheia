from __future__ import annotations

from app.db.session import SessionLocal
from app.evaluation.runner import run_offline_evaluation


def run_evaluation_job(
    name: str,
    retrieval_mode: str | None = None,
    dataset_name: str = "beir/scifact",
    dataset_version: str = "test",
    index_version_id: str | None = None,
    query_limit: int | None = None,
    query_offset: int = 0,
    top_k: int = 10,
    candidate_k: int | None = None,
    bm25_candidate_k: int | None = None,
    dense_candidate_k: int | None = None,
    hybrid_candidate_k: int | None = None,
    rerank_top_n: int | None = None,
    rrf_k: int = 60,
    notes: str | None = None,
    experiment_config_id: str | None = None,
    experiment_config_name: str | None = None,
    rq_job_id: str | None = None,
) -> dict:
    db = SessionLocal()
    try:
        return run_offline_evaluation(
            db,
            name=name,
            retrieval_mode=retrieval_mode,
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            index_version_id=index_version_id,
            query_limit=query_limit,
            query_offset=query_offset,
            top_k=top_k,
            candidate_k=candidate_k,
            bm25_candidate_k=bm25_candidate_k,
            dense_candidate_k=dense_candidate_k,
            hybrid_candidate_k=hybrid_candidate_k,
            rerank_top_n=rerank_top_n,
            rrf_k=rrf_k,
            notes=notes,
            experiment_config_id=experiment_config_id,
            experiment_config_name=experiment_config_name,
        )
    finally:
        db.close()
