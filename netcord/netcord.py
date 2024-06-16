import secrets
from fastapi import Request, Depends
from datetime import datetime, timezone

from aiohttp import BasicAuth
from urllib.parse import urlencode, quote

from netcord.http import HTTPClient
from netcord.singletons import SingletonMeta

from netcord.utils import login_required
from netcord.models import Token, User, Guild
from netcord.exceptions import Unauthorized, Forbidden, \
    InternalServerError, ScopeMissing

from netcord.logger import get_logger
logger = get_logger(__name__)


class Netcord(HTTPClient, metaclass=SingletonMeta):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        bot_token: str = None,
        redirect_uri: str = 'http://127.0.0.1:8000/callback',
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

        self.token = f'{self.api}/oauth2/token'
        self.revoke = f'{self.api}/oauth2/token/revoke'

    # auth
    def generate_auth_url(self, session_id: str = None) -> str:
        query_params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self.scopes,
        }

        if session_id:
            state = secrets.token_urlsafe(16)
            self.state_storage[session_id] = state

            query_params.update({'state': state})

        return f'{self.authorize}?{urlencode(query_params, quote_via=quote)}'

    def check_received_state(self, session_id: str, state: str) -> None:
        stored_state = self.state_storage.pop(session_id, None)

        if stored_state is None:
            raise Forbidden

        if stored_state != state:
            raise Forbidden

        pass

    async def is_authenticated(self, access_token: str = Depends(login_required)):  # noqa
        headers = {'Authorization': 'Bearer ' + access_token}

        route = self.api + '/oauth2/@me'
        response: dict = await self.fetch('GET', route, headers)

        if response is None:
            raise InternalServerError

        expires = response.get('expires', None)
        if expires is None:
            raise Unauthorized

        expires = datetime.fromisoformat(expires)
        if expires <= datetime.now(timezone.utc):
            raise Unauthorized

        pass

    async def extract_callback_data(self, request: Request) -> str:
        data = dict(await request.form())

        session_id = data.get('session_id', None)
        state = data.get('state', None)

        if session_id and state:
            self.check_received_state(session_id, state)

        code = data.get('code', None)
        if not code:
            raise Forbidden

        return code

    # tokens
    async def _get_tokens(self, url: str, data: dict, return_class=None):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return await self.fetch('POST', url, headers=headers, data=data, # noqa
                                auth=self.auth, return_class=return_class)

    async def get_access_token(self, code: str) -> Token:
        data = {
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }

        return await self._get_tokens(self.token, data, Token)

    async def refresh_access_token(self, refresh_token: str) -> Token:
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        return await self._get_tokens(self.token, data, Token)

    async def revoke_access_token(self, access_token: str) -> None:
        data = {
            'token': access_token,
            'token_type_hint': 'access_token'
        }

        return await self._get_tokens(self.revoke, data, None)

    # users
    async def get_user(self, access_token: str) -> User:
        if 'identify' not in self.scopes:
            raise ScopeMissing('identify')

        route = self.api + '/users/@me'
        headers = {'Authorization': 'Bearer ' + access_token}

        user = await self.fetch('GET', route, headers, return_class=User)
        if not user:
            raise Unauthorized

        return user

    async def get_user_by_id(self, user_id: str) -> User:
        if not self.bot_token:
            raise ValueError('Bot token is required')

        route = self.api + f'/users/{user_id}'
        headers = {'Authorization': 'Bot ' + self.bot_token}

        return await self.fetch('GET', route, headers, return_class=User)

    async def get_user_guilds(self, access_token: str) -> list[Guild]:
        if 'guilds' not in self.scopes:
            raise ScopeMissing('guilds')

        route = self.api + '/users/@me/guilds'
        headers = {'Authorization': 'Bearer ' + access_token}

        guilds = await self.fetch('GET', route, headers, return_class=Guild)
        if not guilds:
            raise Unauthorized

        return guilds

    # apps
    async def get_app(self) -> dict:
        if self.bot_token is None:
            raise ValueError('Bot token is required')

        route = self.api + '/applications/@me'
        headers = {'Authorization': 'Bot ' + self.bot_token}

        return await self.fetch('GET', route, headers)
