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
    "services/api/app/api/dependencies/__init__.py",
    "services/api/app/api/dependencies/admin.py",
    "services/api/app/api/v1/routes/admin.py",
    "services/api/app/api/v1/routes/system.py",
    "services/api/app/schemas/admin.py",
    "services/api/app/schemas/health.py",
    "services/api/app/schemas/system.py",
    "services/api/tests/test_health.py",
    "services/api/tests/test_db_health.py",
    "services/api/tests/test_model_metadata.py",
    "services/api/tests/test_jobs.py",
    "services/api/tests/test_system_routes.py",
    "services/api/tests/test_admin_auth.py",
    "scripts/powershell/db-upgrade.ps1",
    "scripts/powershell/db-downgrade.ps1",
    "scripts/powershell/db-current.ps1",
    "scripts/powershell/db-history.ps1",
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
