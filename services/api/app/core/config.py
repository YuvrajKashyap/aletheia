from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.app_mode import is_public_app_mode, validate_admin_key_for_mode


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
    ADMIN_API_KEY: str = "replace-me"
    IR_DATASETS_HOME: str = "data/raw/ir_datasets"
    SCIFACT_CORPUS_DATASET_ID: str = "beir/scifact"
    SCIFACT_EVAL_DATASET_ID: str = "beir/scifact/test"
    SCIFACT_DEFAULT_SPLIT: str = "test"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    OPENSEARCH_URL: str = "http://localhost:9200"
    OPENSEARCH_USERNAME: str | None = None
    OPENSEARCH_PASSWORD: str | None = None
    OPENSEARCH_VERIFY_CERTS: bool = False
    OPENSEARCH_REQUEST_TIMEOUT_SECONDS: int = 30
    LEXICAL_INDEX_BATCH_SIZE: int = 500

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def public_app_mode(self) -> bool:
        return is_public_app_mode(self.APP_MODE)

    @property
    def admin_key_warnings(self) -> list[str]:
        return validate_admin_key_for_mode(self.APP_MODE, self.ADMIN_API_KEY)


@lru_cache
def get_settings() -> Settings:
    return Settings()
