import logging
import os
import socket
import threading
import time
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.system import WorkerHeartbeat
from app.models.mixins import utc_now

logger = logging.getLogger(__name__)


def record_worker_heartbeat(
    worker_name: str,
    queue_name: str | None,
    status: str,
    current_job_id: str | None = None,
    metadata_json: dict | None = None,
) -> None:
    try:
        with SessionLocal() as db:
            heartbeat = db.scalar(
                select(WorkerHeartbeat).where(WorkerHeartbeat.worker_name == worker_name)
            )
            now = utc_now()
            if heartbeat is None:
                heartbeat = WorkerHeartbeat(
                    worker_name=worker_name,
                    queue_name=queue_name,
                    status=status,
                    current_job_id=current_job_id,
                    metadata_json=metadata_json or {},
                    last_seen_at=now,
                )
                db.add(heartbeat)
            else:
                heartbeat.queue_name = queue_name
                heartbeat.status = status
                heartbeat.current_job_id = current_job_id
                heartbeat.metadata_json = metadata_json or {}
                heartbeat.last_seen_at = now
                heartbeat.updated_at = now

            db.commit()
    except Exception:
        logger.exception("Failed to record worker heartbeat")


def _heartbeat_metadata() -> dict[str, Any]:
    return {
        "process_id": os.getpid(),
        "hostname": socket.gethostname(),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


def start_heartbeat_loop(
    worker_name: str,
    queue_name: str | None,
    interval_seconds: int,
) -> threading.Thread:
    def run() -> None:
        while True:
            record_worker_heartbeat(
                worker_name=worker_name,
                queue_name=queue_name,
                status="running",
                metadata_json=_heartbeat_metadata(),
            )
            time.sleep(interval_seconds)

    thread = threading.Thread(
        target=run,
        name=f"{worker_name}-heartbeat",
        daemon=True,
    )
    thread.start()
    return thread
