"""Standard-library-only diagnostics for the Aletheia repo."""

from __future__ import annotations

import platform
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


EXPECTED_DIRS = [
    "apps/web",
    "services/api",
    "services/api/app",
    "services/api/app/api/v1/routes",
    "services/api/app/core",
    "services/api/app/db",
    "services/api/app/datasets",
    "services/api/app/cli",
    "services/api/app/text",
    "services/api/app/chunking",
    "services/api/app/ml",
    "services/api/app/search",
    "services/api/app/ingestion",
    "services/api/app/indexing",
    "services/api/app/models",
    "services/api/app/schemas",
    "services/api/alembic",
    "services/api/alembic/versions",
    "services/api/tests",
    "services/worker",
    "infra",
    "data",
    "docs",
    "scripts",
    "tests",
]

EXPECTED_FILES = [
    "PROJECT_CHARTER.md",
    "AGENTS.md",
    "docs/product-spec.md",
    "docs/dev-commands.md",
    ".env.example",
    ".gitignore",
    "docker-compose.yml",
    "services/api/pyproject.toml",
    "services/api/alembic.ini",
    "services/api/alembic/env.py",
    "services/api/alembic/script.py.mako",
    "services/api/alembic/versions/0001_initialize_database.py",
    "services/api/alembic/versions/0002_create_core_schema.py",
    "services/api/app/main.py",
    "services/api/app/api/v1/router.py",
    "services/api/app/api/v1/routes/health.py",
    "services/api/app/core/config.py",
    "services/api/app/core/app_mode.py",
    "services/api/app/core/logging.py",
    "services/api/app/core/middleware.py",
    "services/api/app/core/redis.py",
    "services/api/app/db/base.py",
    "services/api/app/db/session.py",
    "services/api/app/db/health.py",
    "services/api/app/models/__init__.py",
    "services/api/app/models/mixins.py",
    "services/api/app/models/datasets.py",
    "services/api/app/models/indexing.py",
    "services/api/app/models/queries.py",
    "services/api/app/models/experiments.py",
    "services/api/app/models/evaluation.py",
    "services/api/app/models/system.py",
    "services/api/app/jobs/__init__.py",
    "services/api/app/jobs/health.py",
    "services/api/app/jobs/queue.py",
    "services/api/app/worker/__init__.py",
    "services/api/app/worker/runner.py",
    "services/api/app/worker/heartbeat.py",
    "services/api/app/datasets/__init__.py",
    "services/api/app/datasets/scifact.py",
    "services/api/app/cli/__init__.py",
    "services/api/app/cli/load_scifact.py",
    "services/api/app/cli/chunk_documents.py",
    "services/api/app/text/__init__.py",
    "services/api/app/text/normalization.py",
    "services/api/app/text/chunking.py",
    "services/api/app/text/hashing.py",
    "services/api/app/chunking/__init__.py",
    "services/api/app/chunking/service.py",
    "services/api/app/ml/__init__.py",
    "services/api/app/ml/embeddings.py",
    "services/api/app/search/__init__.py",
    "services/api/app/search/opensearch_client.py",
    "services/api/app/search/qdrant_client.py",
    "services/api/app/search/lexical_mapping.py",
    "services/api/app/search/lexical_indexer.py",
    "services/api/app/search/vector_indexer.py",
    "services/api/app/search/retrieval_models.py",
    "services/api/app/search/fusion.py",
    "services/api/app/search/lexical_retriever.py",
    "services/api/app/search/dense_retriever.py",
    "services/api/app/search/hybrid_retriever.py",
    "services/api/app/search/service.py",
    "services/api/app/ingestion/__init__.py",
    "services/api/app/ingestion/statuses.py",
    "services/api/app/ingestion/service.py",
    "services/api/app/ingestion/jobs.py",
    "services/api/app/indexing/__init__.py",
    "services/api/app/indexing/statuses.py",
    "services/api/app/indexing/service.py",
    "services/api/app/indexing/jobs.py",
    "services/api/app/cli/build_lexical_index.py",
    "services/api/app/cli/build_vector_index.py",
    "services/api/app/cli/search_bm25.py",
    "services/api/app/cli/search_dense.py",
    "services/api/app/cli/search_hybrid.py",
    "services/api/app/cli/embed_text.py",
    "services/api/app/api/dependencies/__init__.py",
    "services/api/app/api/dependencies/admin.py",
    "services/api/app/api/v1/routes/admin.py",
    "services/api/app/api/v1/routes/datasets.py",
    "services/api/app/api/v1/routes/indexes.py",
    "services/api/app/api/v1/routes/ingestion.py",
    "services/api/app/api/v1/routes/search.py",
    "services/api/app/api/v1/routes/system.py",
    "services/api/app/schemas/admin.py",
    "services/api/app/schemas/datasets.py",
    "services/api/app/schemas/ingestion.py",
    "services/api/app/schemas/indexes.py",
    "services/api/app/schemas/search.py",
    "services/api/app/schemas/health.py",
    "services/api/app/schemas/system.py",
    "services/api/tests/test_health.py",
    "services/api/tests/test_db_health.py",
    "services/api/tests/test_model_metadata.py",
    "services/api/tests/test_jobs.py",
    "services/api/tests/test_system_routes.py",
    "services/api/tests/test_admin_auth.py",
    "services/api/tests/test_scifact_loader.py",
    "services/api/tests/test_dataset_routes.py",
    "services/api/tests/test_text_processing.py",
    "services/api/tests/test_chunking_service.py",
    "services/api/tests/test_ingestion_service.py",
    "services/api/tests/test_ingestion_routes.py",
    "services/api/tests/test_indexing_statuses.py",
    "services/api/tests/test_indexing_service.py",
    "services/api/tests/test_index_routes.py",
    "scripts/powershell/db-upgrade.ps1",
    "scripts/powershell/db-downgrade.ps1",
    "scripts/powershell/db-current.ps1",
    "scripts/powershell/db-history.ps1",
    "scripts/powershell/ingest-scifact.ps1",
    "scripts/powershell/chunk-documents.ps1",
    "scripts/powershell/start-scifact-ingestion-job.ps1",
    "scripts/powershell/create-index-version.ps1",
    "scripts/powershell/index-status.ps1",
    "scripts/powershell/activate-index-version.ps1",
    "scripts/powershell/build-lexical-index.ps1",
    "scripts/powershell/start-lexical-index-build-job.ps1",
    "scripts/powershell/build-vector-index.ps1",
    "scripts/powershell/start-vector-index-build-job.ps1",
    "scripts/powershell/search-bm25.ps1",
    "scripts/powershell/search-dense.ps1",
    "scripts/powershell/search-hybrid.ps1",
    "scripts/powershell/search-api.ps1",
    "scripts/powershell/embed-text.ps1",
    "scripts/powershell/worker.ps1",
    "scripts/powershell/enqueue-test-job.ps1",
    "scripts/powershell/admin-status.ps1",
]


def status_line(status: str, label: str, detail: str = "") -> None:
    if detail:
        print(f"{status:<4} {label:<55} {detail}")
    else:
        print(f"{status:<4} {label}")


def check_path(path_text: str, should_be_dir: bool) -> bool:
    path = PROJECT_ROOT / path_text

    if should_be_dir:
        exists = path.is_dir()
        kind = "directory"
    else:
        exists = path.is_file()
        kind = "file"

    if exists:
        status_line("PASS", path_text, f"{kind} exists")
        return True

    status_line("WARN", path_text, f"missing expected {kind}")
    return False


def main() -> int:
    print()
    print("Aletheia doctor")
    print("================")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print()

    print("Expected folders")
    print("----------------")
    dir_results = [check_path(path, should_be_dir=True) for path in EXPECTED_DIRS]

    print()
    print("Expected files")
    print("--------------")
    file_results = [check_path(path, should_be_dir=False) for path in EXPECTED_FILES]

    print()
    if all(dir_results) and all(file_results):
        print("PASS Aletheia repo structure looks ready for the current step.")
        return 0

    print("WARN Aletheia repo structure has missing expected items.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
