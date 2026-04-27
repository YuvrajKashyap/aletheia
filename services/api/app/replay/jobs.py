from __future__ import annotations

from app.db.session import SessionLocal
from app.replay.service import run_golden_query_replay, run_saved_query_replay


def run_saved_query_replay_job(
    saved_query_id: str,
    retrieval_mode: str | None = None,
    experiment_config_id: str | None = None,
    experiment_config_name: str | None = None,
    index_version_id: str | None = None,
    source_trace_id: str | None = None,
    top_k: int = 10,
    candidate_k: int | None = None,
    bm25_candidate_k: int | None = None,
    dense_candidate_k: int | None = None,
    hybrid_candidate_k: int | None = None,
    rerank_top_n: int | None = None,
    rrf_k: int = 60,
    rq_job_id: str | None = None,
) -> dict:
    db = SessionLocal()
    try:
        return run_saved_query_replay(
            db,
            saved_query_id=saved_query_id,
            retrieval_mode=retrieval_mode,
            experiment_config_id=experiment_config_id,
            experiment_config_name=experiment_config_name,
            index_version_id=index_version_id,
            source_trace_id=source_trace_id,
            top_k=top_k,
            candidate_k=candidate_k,
            bm25_candidate_k=bm25_candidate_k,
            dense_candidate_k=dense_candidate_k,
            hybrid_candidate_k=hybrid_candidate_k,
            rerank_top_n=rerank_top_n,
            rrf_k=rrf_k,
            started_by="rq",
        )
    finally:
        db.close()


def run_golden_query_replay_job(
    name: str,
    source: str = "golden_scifact",
    retrieval_mode: str | None = None,
    experiment_config_id: str | None = None,
    experiment_config_name: str | None = None,
    limit: int | None = None,
    offset: int = 0,
    top_k: int = 10,
    candidate_k: int | None = None,
    bm25_candidate_k: int | None = None,
    dense_candidate_k: int | None = None,
    hybrid_candidate_k: int | None = None,
    rerank_top_n: int | None = None,
    rrf_k: int = 60,
    notes: str | None = None,
    rq_job_id: str | None = None,
) -> dict:
    db = SessionLocal()
    try:
        return run_golden_query_replay(
            db,
            name=name,
            source=source,
            retrieval_mode=retrieval_mode,
            experiment_config_id=experiment_config_id,
            experiment_config_name=experiment_config_name,
            limit=limit,
            offset=offset,
            top_k=top_k,
            candidate_k=candidate_k,
            bm25_candidate_k=bm25_candidate_k,
            dense_candidate_k=dense_candidate_k,
            hybrid_candidate_k=hybrid_candidate_k,
            rerank_top_n=rerank_top_n,
            rrf_k=rrf_k,
            notes=notes,
        )
    finally:
        db.close()
