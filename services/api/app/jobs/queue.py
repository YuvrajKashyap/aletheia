from typing import Any

from redis.exceptions import RedisError
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from app.core.config import get_settings
from app.core.redis import get_redis_connection
from app.ingestion.jobs import run_scifact_ingestion_job
from app.indexing.jobs import build_lexical_index_job, build_vector_index_job
from app.jobs.health import ping_job


def _serialize_datetime(value: Any) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _serialize_status(value: Any) -> str:
    return getattr(value, "value", str(value))


def _serialize_job(job: Job, *, found: bool = True) -> dict:
    exc_info = getattr(job, "exc_info", None)
    return {
        "found": found,
        "job_id": job.id,
        "status": _serialize_status(job.get_status(refresh=True)),
        "result": job.result if isinstance(job.result, dict) else None,
        "error": exc_info,
        "enqueued_at": _serialize_datetime(getattr(job, "enqueued_at", None)),
        "ended_at": _serialize_datetime(getattr(job, "ended_at", None)),
    }


def get_queue(queue_name: str | None = None) -> Queue:
    settings = get_settings()
    return Queue(queue_name or settings.RQ_DEFAULT_QUEUE, connection=get_redis_connection())


def get_queue_status(queue_name: str | None = None) -> dict:
    queue = get_queue(queue_name)
    return {
        "queue": queue.name,
        "job_count": len(queue),
    }


def enqueue_ping_job(message: str = "pong") -> dict:
    queue = get_queue()
    job = queue.enqueue(ping_job, message)
    return {
        "job_id": job.id,
        "queue": queue.name,
        "status": _serialize_status(job.get_status(refresh=True)),
    }


def enqueue_scifact_ingestion_job(
    ingestion_run_id: str,
    document_limit: int | None = None,
    query_limit: int | None = None,
    qrel_limit: int | None = None,
    split: str = "test",
    chunk_after_load: bool = True,
    chunk_document_limit: int | None = None,
    dry_run: bool = False,
    started_by: str = "api",
) -> dict:
    queue = get_queue()
    job = queue.enqueue(
        run_scifact_ingestion_job,
        document_limit=document_limit,
        query_limit=query_limit,
        qrel_limit=qrel_limit,
        split=split,
        chunk_after_load=chunk_after_load,
        chunk_document_limit=chunk_document_limit,
        dry_run=dry_run,
        started_by=started_by,
        ingestion_run_id=ingestion_run_id,
    )
    return {
        "job_id": job.id,
        "queue": queue.name,
        "status": _serialize_status(job.get_status(refresh=True)),
        "ingestion_run_id": ingestion_run_id,
        "message": "SciFact ingestion job enqueued.",
    }


def enqueue_lexical_index_build_job(
    index_version_id: str,
    recreate: bool = False,
    limit: int | None = None,
    refresh: bool = True,
) -> dict:
    queue = get_queue()
    job = queue.enqueue(
        build_lexical_index_job,
        index_version_id=index_version_id,
        recreate=recreate,
        limit=limit,
        refresh=refresh,
    )
    return {
        "job_id": job.id,
        "queue": queue.name,
        "status": _serialize_status(job.get_status(refresh=True)),
        "index_version_id": index_version_id,
        "message": "Lexical index build job enqueued.",
    }


def enqueue_vector_index_build_job(
    index_version_id: str,
    recreate: bool = False,
    limit: int | None = None,
    batch_size: int | None = None,
) -> dict:
    queue = get_queue()
    job = queue.enqueue(
        build_vector_index_job,
        index_version_id=index_version_id,
        recreate=recreate,
        limit=limit,
        batch_size=batch_size,
    )
    return {
        "job_id": job.id,
        "queue": queue.name,
        "status": _serialize_status(job.get_status(refresh=True)),
        "index_version_id": index_version_id,
        "message": "Vector index build job enqueued.",
    }


def get_job_status(job_id: str) -> dict:
    try:
        job = Job.fetch(job_id, connection=get_redis_connection())
    except NoSuchJobError:
        return {
            "found": False,
            "job_id": job_id,
            "status": None,
            "result": None,
            "error": None,
            "enqueued_at": None,
            "ended_at": None,
        }
    except RedisError as exc:
        return {
            "found": False,
            "job_id": job_id,
            "status": None,
            "result": None,
            "error": str(exc),
            "enqueued_at": None,
            "ended_at": None,
        }

    return _serialize_job(job)
