import jwt
import datetime

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
oauth2 = OAuth2PasswordBearer('token')

from netcord.enums import TokenType
from netcord.exceptions import Unauthorized

from netcord.logger import get_logger
logger = get_logger(__name__)


class JWTClient:
    def __init__(
        self,
        secret_key: str,
        algorithm: str = 'HS256',
        access_token_expires_in: int = 30,
        refresh_token_expires_in: int = 7
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expires_in = access_token_expires_in  # minutes
        self.refresh_token_expires_in = refresh_token_expires_in  # days

    def create_token(self, data: dict, token_type: TokenType) -> str:
        to_encode = data.copy()

        if token_type.value == 'access':
            expire = datetime.datetime.now(
                datetime.UTC) + datetime.timedelta(
                    minutes=self.access_token_expires_in)

        elif token_type.value == 'refresh':
            expire = datetime.datetime.now(
                datetime.UTC) + datetime.timedelta(
                    days=self.refresh_token_expires_in)
        else:
            raise ValueError('Only access or refresh token type possible')

        to_encode.update({'exp': expire, 'type': token_type.value})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, [self.algorithm])
            return payload

        except jwt.ExpiredSignatureError as error:
            raise Unauthorized(str(error))
        except jwt.InvalidTokenError as error:
            raise Unauthorized(str(error))

    def exchange_refresh_token(self, refresh_token: str) -> tuple[str, str]:
        payload = self.decode_token(refresh_token)
        if payload.get('type') != 'refresh':
            raise HTTPException(400, 'The token type is required to be refresh')

        id, username = payload['id'], payload['username']
        data = {'id': id, 'username': username}

        new_access_token = self.create_token(data, TokenType.ACCESS)
        new_refresh_token = self.create_token(data, TokenType.REFRESH)

        return (new_access_token, new_refresh_token)
