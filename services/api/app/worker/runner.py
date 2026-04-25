import logging
import os

from rq import Queue, SimpleWorker, Worker

from app.core.config import get_settings
from app.core.redis import get_redis_connection
from app.worker.heartbeat import start_heartbeat_loop


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    settings = get_settings()
    redis_connection = get_redis_connection()
    queue = Queue(settings.RQ_DEFAULT_QUEUE, connection=redis_connection)
    worker_class = SimpleWorker if os.name == "nt" else Worker
    worker = worker_class([queue], connection=redis_connection, name=settings.WORKER_NAME)

    start_heartbeat_loop(
        worker_name=settings.WORKER_NAME,
        queue_name=settings.RQ_DEFAULT_QUEUE,
        interval_seconds=settings.WORKER_HEARTBEAT_INTERVAL_SECONDS,
    )

    logger.info(
        "Starting Aletheia worker name=%s queue=%s",
        settings.WORKER_NAME,
        settings.RQ_DEFAULT_QUEUE,
    )
    worker.work()


if __name__ == "__main__":
    main()
