import secrets

from aiohttp import BasicAuth
from urllib.parse import urlencode, quote

from fastapi import Request, Depends
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials as HTTPAuth

from netcord.http import HTTPClient
from netcord.models import Token, User, Guild
from netcord.exceptions import Unauthorized, Forbidden, ScopeMissing


class Netcord(HTTPClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        bot_token: str = None,
        redirect_uri: str = 'http://127.0.0.1/callback',
        scopes: str | list[str] = ['identify', 'email', 'guilds']
    ):
        super().__init__()

        self.client_id = client_id
        self.client_secret = client_secret

        self.bot_token = bot_token

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

    # auth
    def generate_auth_url(self, session_id: str = None) -> str:
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self.scopes,
        }

        if session_id:
            state = secrets.token_urlsafe(16)
            self.state_storage[session_id] = state

            params.update({'state': state})

        return f'{self.authorize}?{urlencode(params, quote_via=quote)}'
    
    def check_state(self, session_id: str, received_state: str):
        stored_state = self.state_storage.pop(session_id, None)

        if stored_state is None:
            raise Forbidden
        
        if stored_state != received_state:
            raise Forbidden
        
        return True

    async def check_token(self, request: Request) -> str | None:
        header = request.headers.get('Authorization')
        if not header:
            raise Unauthorized
        
        parts = header.split(' ')
        if parts[0] != 'Bearer' or len(parts) > 2:
            raise Unauthorized
        
        token = parts[1]
        return token

    async def login_required(self, bearer: HTTPAuth = Depends(HTTPBearer())):
        if bearer is None:
            raise Unauthorized
        if not await self.is_authenticated(bearer.credentials):
            raise Unauthorized
        
    async def is_authenticated(self, access_token: str) -> bool:
        headers = {'Authorization': 'Bearer ' + access_token}
        route = self.api + '/oauth2/@me'

        try:
            res = await self.fetch('GET', route, headers)
            print(res)

            return True
        except Unauthorized:
            return False

    # tokens
    async def _tokens(self, url: str, data: dict, return_class=None):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return await self.fetch('POST', url, headers=headers, data=data, 
                                auth=self.auth, return_class=return_class)

    async def get_access_token(self, code: str) -> Token:
        data = {
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }

        return await self._tokens(self.token, data, Token)

    async def refresh_access_token(self, refresh_token: str) -> Token:
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        return await self._tokens(self.token, data, Token)

    async def revoke_access_token(self, access_token: str) -> None:
        data = {
            'token': access_token,
            'token_type_hint': 'access_token'
        }

        return await self._tokens(self.revoke, data, None)
    
    # users
    async def get_user(self, request: Request) -> User:
        access_token = await self.check_token(request)

        if 'identify' not in self.scopes:
            raise ScopeMissing('identify')
        
        route = self.api + '/users/@me'
        headers = {'Authorization': 'Bearer ' + access_token}

        return await self.fetch('GET', route, headers, return_class=User)

    async def get_user_by_id(self, user_id: str) -> User:
        if not self.bot_token:
            raise ValueError('Bot token is required')

        route = self.api + f'/users/{user_id}'
        headers = {'Authorization': 'Bot ' + self.bot_token}

        return await self.fetch('GET', route, headers, return_class=User)

    async def get_user_guilds(self, request: Request) -> list[Guild]:
        access_token = await self.check_token(request)

        if 'guilds' not in self.scopes:
            raise ScopeMissing('guilds')
        
        route = self.api + '/users/@me/guilds'
        headers = {'Authorization': 'Bearer ' + access_token}

        return await self.fetch('GET', route, headers, return_class=Guild)

    # apps
    async def get_app(self) -> dict:
        if self.bot_token is None:
            raise ValueError('Bot token is required')

        route = self.api + '/applications/@me'
        headers = {'Authorization': 'Bot ' + self.bot_token}

        return await self.fetch('GET', route, headers)
