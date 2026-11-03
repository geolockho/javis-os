"""Rate limit trong bộ nhớ (app chạy 1 replica, 1 worker nên không cần Redis)."""
from __future__ import annotations

import threading
import time


class TokenBucket:
    """Mỗi key một xô: tối đa `capacity` lượt, nạp lại `rate` lượt/giây."""

    def __init__(self, rate: float, capacity: float, max_keys: int = 50_000):
        self.rate = float(rate)
        self.capacity = float(capacity)
        self.max_keys = max_keys
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        with self._lock:
            tokens, last = self._buckets.get(key, (self.capacity, now))
            tokens = min(self.capacity, tokens + (now - last) * self.rate)
            if tokens < 1.0:
                self._buckets[key] = (tokens, now)
                return False
            self._buckets[key] = (tokens - 1.0, now)
            if len(self._buckets) > self.max_keys:
                self._evict(now)
            return True

    def _evict(self, now: float) -> None:
        # Bỏ các xô đã đầy lại (không còn ý nghĩa giữ)
        full_after = self.capacity / self.rate if self.rate else 0
        stale = [k for k, (_, last) in self._buckets.items() if now - last > full_after]
        for k in stale:
            del self._buckets[k]


def per_second(rate: float) -> TokenBucket:
    return TokenBucket(rate=rate, capacity=max(rate, 1.0))


def per_minute(count: int) -> TokenBucket:
    return TokenBucket(rate=count / 60.0, capacity=max(count, 1))
