"""
In-memory cache for fast UI operations.
LRU + TTL based cache.
"""

import time
import threading
from typing import Any, Optional


class CacheEntry:
    def __init__(self, value: Any, ttl: float):
        self.value = value
        self.expire_at = time.time() + ttl


class LRUCache:
    """
    Simple thread-safe LRU cache with TTL.
    """

    def __init__(self, max_size: int = 128, ttl_sec: float = 300):
        self.max_size = max_size
        self.ttl_sec = ttl_sec
        self.data = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            entry = self.data.get(key)
            if not entry:
                return None
            if entry.expire_at < time.time():
                del self.data[key]
                return None
            return entry.value

    def set(self, key: str, value: Any):
        with self.lock:
            if len(self.data) >= self.max_size:
                # remove random-oldest
                k = next(iter(self.data))
                del self.data[k]
            self.data[key] = CacheEntry(value, self.ttl_sec)

    def clear(self):
        with self.lock:
            self.data.clear()
