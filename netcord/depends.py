from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .errors import AuthenticationError

http_bearer = HTTPBearer(auto_error=False)

__all__ = (
    'authenticated'
)


def authenticated(
    header: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    if not (header and header.scheme and header.credentials):
        raise AuthenticationError
    
    if header.scheme.lower() != 'bearer':
        raise AuthenticationError(
            detail='Invalid authentication scheme'
        )
