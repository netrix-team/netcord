from fastapi import HTTPException


class Unauthorized(HTTPException):
    """An Exception raised when a user is not authorized"""

    def __init__(self, detail: str = 'Unauthorized'):
        super().__init__(status_code=401, detail=detail)


class InvalidRequest(HTTPException):
    """An Exception raised when a request is not valid"""

    def __init__(self, detail: str = 'InvalidRequest'):
        super().__init__(status_code=400, detail=detail)


class Forbidden(HTTPException):
    """An Exception raised when a user is denied access"""

    def __init__(self, detail: str = 'Forbidden'):
        super().__init__(status_code=403, detail=detail)


class ScopeMissing(Exception):
    """An Exception raised when a required scope has not been transferred"""

    def __init__(self, scope: str):
        super().__init__(f'Required scope <{scope}> is missing')
