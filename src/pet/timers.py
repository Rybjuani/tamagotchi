from __future__ import annotations

import time
from datetime import UTC, datetime


class RealtimeClock:
    def __init__(self) -> None:
        self._last = time.monotonic()

    def reset(self) -> None:
        self._last = time.monotonic()

    def consume(self) -> float:
        now = time.monotonic()
        delta = now - self._last
        self._last = now
        return max(0.0, delta)


def seconds_since_iso(timestamp: str) -> float:
    try:
        previous = datetime.fromisoformat(timestamp)
    except ValueError:
        return 0.0
    if previous.tzinfo is None:
        previous = previous.replace(tzinfo=UTC)
    return max(0.0, (datetime.now(UTC) - previous.astimezone(UTC)).total_seconds())


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()
