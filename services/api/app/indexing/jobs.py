from __future__ import annotations

from uuid import UUID

from rq import get_current_job

from app.db.session import SessionLocal
from app.search.lexical_indexer import build_lexical_index_for_version
from app.search.opensearch_client import get_opensearch_client


def build_lexical_index_job(
    index_version_id: str,
    recreate: bool = False,
    limit: int | None = None,
    refresh: bool = True,
    rq_job_id: str | None = None,
) -> dict:
    db = SessionLocal()
    try:
        current_job = get_current_job()
        resolved_rq_job_id = rq_job_id or (current_job.id if current_job else None)
        client = get_opensearch_client()
        return build_lexical_index_for_version(
            db,
            client,
            index_version_id=UUID(index_version_id),
            recreate=recreate,
            limit=limit,
            refresh=refresh,
            rq_job_id=resolved_rq_job_id,
        )
    finally:
        db.close()
