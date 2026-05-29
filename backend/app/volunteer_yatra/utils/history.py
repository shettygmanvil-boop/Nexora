"""Application status history helpers."""

from datetime import datetime, timezone
from uuid import UUID


def append_status_history(
    history: list,
    status: str,
    by_user_id: UUID | None = None,
    note: str | None = None,
) -> list:
    entry = {
        "status": status,
        "at": datetime.now(timezone.utc).isoformat(),
        "by_user_id": str(by_user_id) if by_user_id else None,
        "note": note,
    }
    return [*history, entry]
