from datetime import datetime, timezone


def ping_job(message: str = "pong") -> dict:
    return {
        "status": "ok",
        "message": message,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
