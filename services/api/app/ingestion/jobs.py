from uuid import UUID

from app.db.session import SessionLocal
from app.ingestion.service import run_scifact_ingestion


def run_scifact_ingestion_job(
    document_limit: int | None = None,
    query_limit: int | None = None,
    qrel_limit: int | None = None,
    split: str = "test",
    chunk_after_load: bool = True,
    chunk_document_limit: int | None = None,
    dry_run: bool = False,
    started_by: str = "api",
    rq_job_id: str | None = None,
    ingestion_run_id: str | None = None,
) -> dict:
    with SessionLocal() as db:
        return run_scifact_ingestion(
            db,
            document_limit=document_limit,
            query_limit=query_limit,
            qrel_limit=qrel_limit,
            split=split,
            chunk_after_load=chunk_after_load,
            chunk_document_limit=chunk_document_limit,
            dry_run=dry_run,
            started_by=started_by,
            rq_job_id=rq_job_id,
            ingestion_run_id=UUID(ingestion_run_id) if ingestion_run_id else None,
        )
