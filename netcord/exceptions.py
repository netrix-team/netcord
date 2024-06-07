from fastapi import HTTPException


class Unauthorized(HTTPException):
    """An Exception raised when user is not authorized"""

    def __init__(self, detail: str = 'Unauthorized'):
        super().__init__(status_code=401, detail=detail)


class ScopeMissing(Exception):
    """An Exception raised when a required scope has not been transferred"""

    def __init__(self, scope: str):
        super().__init__(f'Required scope <{scope}> is missing')
