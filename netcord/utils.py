from fastapi import Depends
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from netcord.exceptions import Forbidden
http_bearer = HTTPBearer(auto_error=False)


def login_required(
    header: HTTPAuthorizationCredentials = Depends(http_bearer)):

    if not (header and header.scheme and header.credentials):
        raise Forbidden

    if header.scheme.lower() != 'bearer':
        raise Forbidden

    return header.credentials
