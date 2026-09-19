"""Small in-process rate limiter. Use Redis when running multiple workers."""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.lock = Lock()

    def check(self, request: Request) -> None:
        key = request.client.host if request.client else "unknown"
        now = monotonic()
        with self.lock:
            timestamps = self.requests[key]
            while timestamps and timestamps[0] <= now - self.window:
                timestamps.popleft()
            if len(timestamps) >= self.limit:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(self.window)},
                )
            timestamps.append(now)
