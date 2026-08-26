"""
Market Data Cache

Local file-based + optional Redis caching for market data to reduce
API calls to Yahoo Finance / Alpha Vantage.

Strategy:
- In-memory dict for the current process (fastest)
- Local parquet/CSV files on disk for persistent caching across restarts
- Optional Redis for shared cache (if REDIS_URL configured)
"""

import hashlib
import json
import logging
import os
import pickle
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from backend.core.config import settings

logger = logging.getLogger(__name__)


class MarketDataCache:
    """Caches market data locally and optionally in Redis."""

    def __init__(self, cache_path: Optional[str] = None, ttl_hours: int = 24):
        self.cache_path = Path(cache_path or settings.market_data_cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        self._memory: Dict[str, Dict[str, Any]] = {}
        self._redis = None
        self._init_redis()

    def _init_redis(self) -> None:
        """Initialize Redis client if configured (optional)."""
        if settings.redis_url:
            try:
                import redis

                self._redis = redis.from_url(settings.redis_url, decode_responses=False)
                self._redis.ping()
                logger.info("Redis cache enabled at %s", settings.redis_url)
            except Exception as exc:  # pragma: no cover
                logger.warning("Redis unavailable, falling back to local cache: %s", exc)
                self._redis = None

    def _file_path(self, key: str) -> Path:
        """Compute the file path for a cache key."""
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        return self.cache_path / f"{digest}.pkl"

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached value if fresh."""
        # 1. Memory
        if key in self._memory:
            entry = self._memory[key]
            if time.time() - entry["ts"] < self.ttl_hours * 3600:
                return entry["value"]
            self._memory.pop(key, None)

        # 2. Redis
        if self._redis:
            try:
                raw = self._redis.get(key)
                if raw:
                    entry = pickle.loads(raw)
                    if time.time() - entry["ts"] < self.ttl_hours * 3600:
                        self._memory[key] = entry
                        return entry["value"]
            except Exception as exc:  # pragma: no cover
                logger.warning("Redis get failed: %s", exc)

        # 3. Local file
        fpath = self._file_path(key)
        if fpath.exists():
            try:
                with open(fpath, "rb") as f:
                    entry = pickle.load(f)
                if time.time() - entry["ts"] < self.ttl_hours * 3600:
                    self._memory[key] = entry
                    return entry["value"]
                fpath.unlink(missing_ok=True)
            except Exception as exc:  # pragma: no cover
                logger.warning("Cache read failed for %s: %s", key, exc)

        return None

    def set(self, key: str, value: Any) -> None:
        """Store a value in all available cache layers."""
        entry = {"ts": time.time(), "value": value}

        # Memory
        self._memory[key] = entry

        # Local file
        try:
            fpath = self._file_path(key)
            with open(fpath, "wb") as f:
                pickle.dump(entry, f)
        except Exception as exc:  # pragma: no cover
            logger.warning("Cache write failed for %s: %s", key, exc)

        # Redis
        if self._redis:
            try:
                self._redis.setex(key, self.ttl_hours * 3600, pickle.dumps(entry))
            except Exception as exc:  # pragma: no cover
                logger.warning("Redis set failed: %s", exc)

    def clear(self) -> None:
        """Clear all cached data."""
        self._memory.clear()
        for f in self.cache_path.glob("*.pkl"):
            f.unlink(missing_ok=True)
        if self._redis:
            try:
                self._redis.flushdb()
            except Exception:  # pragma: no cover
                pass


# Singleton cache instance
market_cache = MarketDataCache()
