# ============================================
# CACHE — Système de cache simple en mémoire
# Simule un Redis/Memcached léger
# ============================================

import time
import functools
from typing import Any, Optional, Dict
from threading import Lock


class SimpleCache:
    """Cache LRU avec TTL (Time To Live)"""

    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        self._store:    Dict[str, dict] = {}
        self._max_size  = max_size
        self._default_ttl = default_ttl
        self._lock      = Lock()
        self._hits      = 0
        self._misses    = 0

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self._misses += 1
                return None
            if time.time() > entry['expires_at']:
                del self._store[key]
                self._misses += 1
                return None
            self._hits += 1
            return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            if len(self._store) >= self._max_size:
                # Eviction : supprimer la clé la plus ancienne
                oldest = min(self._store, key=lambda k: self._store[k]['expires_at'])
                del self._store[oldest]
            self._store[key] = {
                'value':      value,
                'expires_at': time.time() + (ttl or self._default_ttl),
                'created_at': time.time()
            }

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def invalidate_pattern(self, pattern: str) -> None:
        with self._lock:
            keys = [k for k in self._store if pattern in k]
            for k in keys:
                del self._store[k]

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return round(self._hits / total * 100, 2) if total > 0 else 0.0

    @property
    def stats(self) -> dict:
        return {
            'hits':     self._hits,
            'misses':   self._misses,
            'hit_rate': self.hit_rate,
            'size':     len(self._store)
        }


# Instance globale
cache = SimpleCache(max_size=200, default_ttl=300)


def cached(key_prefix: str, ttl: int = 300):
    """Décorateur de cache"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{':'.join(str(a) for a in args)}"
            cached_val = cache.get(cache_key)
            if cached_val is not None:
                return cached_val
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
