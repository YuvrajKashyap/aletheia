from redis import Redis

from app.core.config import get_settings


def get_redis_connection() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.REDIS_URL)
