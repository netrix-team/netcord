import secrets
from aiohttp import BasicAuth
from urllib.parse import urlencode, quote

from typing import Optional
from fastapi import Depends

from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from netcord.http import HTTPClient
from netcord.models import Tokens, User, Guild
from netcord.exceptions import ScopeMissing, Unauthorized


class Netcord(HTTPClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        service_bot_token: str = None,
        redirect_uri: str = 'http://127.0.0.1/callback',
        scopes: str | tuple[str] = ('identify', 'email', 'guilds')
    ):
        super().__init__()

        self.client_id = client_id
        self.client_secret = client_secret
        self.service_bot_token = service_bot_token

        self.redirect_uri = redirect_uri
        self.scopes = scopes if isinstance(scopes, str) else ' '.join(scopes)

        self.state_storage = {}
        self.auth = BasicAuth(self.client_id, self.client_secret)

        self.base_url = 'https://discord.com'
        self.cdn = 'https://cdn.discordapp.com'

        self.icons = f'{self.cdn}/icons'
        self.avatars = f'{self.cdn}/avatars'
        self.banners = f'{self.cdn}/banners'

        self.api = f'{self.base_url}/api/v10'
        self.authorize = f'{self.base_url}/oauth2/authorize'

        self.token = f'{self.base_url}/api/oauth2/token'
        self.revoke = f'{self.base_url}/api/oauth2/token/revoke'

    def generate_auth_url(self, session_id: str):
        state = secrets.token_urlsafe(16)
        self.state_storage[session_id] = state

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self.scopes,
            'state': state
        }

        return f'{self.authorize}?{urlencode(params, quote_via=quote)}'

    def check_state(self, session_id: str, received_state: str):
        stored_state = self.state_storage.pop(session_id, None)
        if stored_state is None:
            raise Unauthorized('State not found for the given session ID')
        if stored_state != received_state:
            raise Unauthorized('Invalid state parameter')
        return True

    # tokens
    async def get_access_token(self, code: str) -> Tokens:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        data = {
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }

        return await self.fetch(
            'POST', self.token, headers, data, self.auth, Tokens)

    async def refresh_access_token(self, refresh_token: str) -> Tokens:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}

        return await self.fetch(
            'POST', self.token, headers, data, self.auth, Tokens)

    async def revoke_access_token(self, access_token: str) -> None:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'token': access_token, 'token_type_hint': 'access_token'}

        await self.fetch('POST', self.revoke, headers, data, self.auth)

    # users
    async def get_user(self, access_token: str) -> User:
        if 'identify' not in self.scopes:
            raise ScopeMissing('identify')

        headers = {'Authorization': 'Bearer ' + access_token}
        request_url = self.api + '/users/@me'

        return await self.fetch('GET', request_url, headers, return_class=User)

    async def get_user_by_id(self, user_id: str) -> User:
        if self.service_bot_token is None:
            raise ValueError('Bot token is required')

        headers = {'Authorization': 'Bot ' + self.service_bot_token}
        request_url = self.api + f'/users/{user_id}'

        return await self.fetch('GET', request_url, headers, return_class=User)
    
    # auth
    async def is_authenticated(self, access_token: str) -> bool:
        headers = {'Authorization': 'Bearer ' + access_token}
        request_url = self.api + '/oauth2/@me'

        try:
            res = await self.fetch('GET', request_url, headers)
            print(res)

            return True
        except Unauthorized:
            return False
        
    async def login_required(
        self,
        bearer: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer())
    ):
        if bearer is None:
            raise Unauthorized
        if not await self.is_authenticated(bearer.credentials):
            raise Unauthorized

    # guilds
    async def get_user_guilds(self, access_token: str) -> list[dict]:
        if 'guilds' not in self.scopes:
            raise ScopeMissing('guilds')

        headers = {'Authorization': 'Bearer ' + access_token}
        request_url = self.api + '/users/@me/guilds'

        return await self.fetch('GET', request_url, headers, return_class=Guild)

    # apps
    async def get_app(self) -> dict:
        if self.service_bot_token is None:
            raise ValueError('Bot token is required')

        headers = {'Authorization': 'Bot ' + self.service_bot_token}
        request_url = self.api + '/applications/@me'

        return await self.fetch('GET', request_url, headers)
