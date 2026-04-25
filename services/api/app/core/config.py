from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "aletheia"
    APP_MODE: str = "local"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"
    PROJECT_VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql+psycopg://aletheia:aletheia@localhost:5432/aletheia"
    REDIS_URL: str = "redis://localhost:6379/0"
    RQ_DEFAULT_QUEUE: str = "default"
    WORKER_NAME: str = "aletheia-worker"
    WORKER_HEARTBEAT_INTERVAL_SECONDS: int = 15

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
