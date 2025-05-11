# 🗂️ Caching Utility

Provides simple in-memory caching with TTL.

`@cache` Decorator
Wraps async methods to auto-cache results by identifier.

```python
@cache
async def fetch_user(self, identifier: str, *, cache: bool = True):
    ...
```

!!! Tip
    Netcord caches fetch_user & fetch_guilds for 5 minutes by default. Use cache=False to bypass.

