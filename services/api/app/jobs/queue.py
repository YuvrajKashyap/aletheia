from typing import Any

from redis.exceptions import RedisError
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from app.core.config import get_settings
from app.core.redis import get_redis_connection
from app.evaluation.jobs import run_evaluation_job
from app.experiments.jobs import run_evaluation_comparison_job
from app.ingestion.jobs import run_scifact_ingestion_job
from app.indexing.jobs import build_lexical_index_job, build_vector_index_job
from app.jobs.health import ping_job
from app.replay.jobs import run_golden_query_replay_job, run_saved_query_replay_job


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


def enqueue_evaluation_job(
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
) -> dict:
    queue = get_queue()
    job = queue.enqueue(
        run_evaluation_job,
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
    return {
        "job_id": job.id,
        "queue": queue.name,
        "status": _serialize_status(job.get_status(refresh=True)),
        "retrieval_mode": retrieval_mode,
        "message": "Evaluation job enqueued.",
    }


def enqueue_evaluation_comparison_job(
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
) -> dict:
    queue = get_queue()
    job = queue.enqueue(
        run_evaluation_comparison_job,
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
    return {
        "job_id": job.id,
        "queue": queue.name,
        "status": _serialize_status(job.get_status(refresh=True)),
        "message": "Evaluation comparison job enqueued.",
    }


def enqueue_saved_query_replay_job(
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
) -> dict:
    queue = get_queue()
    job = queue.enqueue(
        run_saved_query_replay_job,
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
    )
    return {
        "job_id": job.id,
        "queue": queue.name,
        "status": _serialize_status(job.get_status(refresh=True)),
        "message": "Saved query replay job enqueued.",
    }


def enqueue_golden_query_replay_job(
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
) -> dict:
    queue = get_queue()
    job = queue.enqueue(
        run_golden_query_replay_job,
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
    return {
        "job_id": job.id,
        "queue": queue.name,
        "status": _serialize_status(job.get_status(refresh=True)),
        "message": "Golden query replay job enqueued.",
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
