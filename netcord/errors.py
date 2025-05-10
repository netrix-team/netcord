from fastapi import HTTPException

__all__ = (
    'NetError',
    'AuthenticationError',
    'TokenExchangeError',
)


class NetError(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class AuthenticationError(NetError):
    def __init__(
        self,
        detail: str = 'Not authenticated',
        status_code: int = 401
    ):
        super().__init__(status_code=status_code, detail=detail)


class TokenExchangeError(NetError):
    def __init__(
        self,
        detail: str = 'Failed to exchange OAuth2 code',
        status_code: int = 400
    ):
        super().__init__(status_code=status_code, detail=detail)
