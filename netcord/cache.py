import time
import functools
from typing import Any, Optional, Tuple

__all__ = (
    'Cache',
    'cache'
)


class Cache:
    def __init__(self, default_ttl: int = 300) -> None:
        self._store: dict[str, Tuple[float, Any]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None

        expires_at, value = entry
        if time.time() > expires_at:
            del self._store[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = self.default_ttl if ttl is None else ttl
        self._store[key] = (time.time() + ttl, value)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


def cache(func):
    @functools.wraps(func)
    async def wrapper(
        self,
        identifier: str, *,
        cache: bool = True,
        cache_ttl: Optional[int] = None
    ):
        cache_key = f'{func.__name__}:{identifier}'
        if cache:
            cached_value = self._cache.get(cache_key)
            if cached_value is not None:
                return cached_value

        result = await func(self, identifier)

        if cache:
            self._cache.set(cache_key, result, ttl=cache_ttl)
        return result

    return wrapper
