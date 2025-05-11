# 🔗 Dependency

FastAPI dependency for bearer auth.

```python
http_bearer = HTTPBearer(auto_error=False)

def authenticated(
    header: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    if not (header and header.scheme and header.credentials):
        raise AuthenticationError

    if header.scheme.lower() != 'bearer':
        raise AuthenticationError(
            detail='Invalid authentication scheme'
        )
```
