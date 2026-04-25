from sqlalchemy import text

from app.db.session import engine


def check_database_health() -> dict[str, str | None]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "postgresql",
            "error": None,
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "database": "postgresql",
            "error": str(exc),
        }
