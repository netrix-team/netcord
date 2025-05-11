## Initialization

```python
Netcord(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: tuple[str, ...] = DEFAULT_SCOPES,
    bot_token: str | None = None
)
```

| Parameter       | Type              | Description                               |
| --------------- | ----------------- | ----------------------------------------- |
| `client_id`     | `str`             | Discord App Client ID                     |
| `client_secret` | `str`             | Discord App Client Secret                 |
| `redirect_uri`  | `str`             | Your OAuth2 redirect URL                  |
| `scopes`        | `tuple[str, ...]` | OAuth2 scopes (default: identify, email…) |
| `bot_token`     | `str | None`      | Bot token for application API (optional)  |

## Methods

- `generate_auth_url(state: str = None, prompt: str = 'consent') → str`

    Generate the Discord authorization URL.

```python
url = netcord.generate_auth_url(state='xyz', prompt='consent')
```

---

- `exchange_code(code: str) → Oauth2Token`

    Exchange an authorization code for [tokens](/reference/models/#oauth2token).

    Raises [TokenExchangeError](reference/errors/#class-tokenexchangeerrorneterror) on failure.

```python
code = 'your code'  # 2mvsjmfv9uaym3thfhdzg
token = exchange_code(code=code)
```

---

- `refresh_token(refresh_token: str) → Oauth2Token`

    Refresh an OAuth2 [token](/reference/models/#oauth2token).

---

- `revoke_token(token: str, token_type_hint: Literal['access_token','refresh_token'] = None) -> bool`

    Revoke an OAuth2 token.

---

## Cached Fetches
- `fetch_user(access_token: str) → User`
- `fetch_guilds(access_token: str) → list[Guild]`
- `fetch_user_by_id(user_id: str) → User`

!!! Info
    All decorated with `@cache` (TTL = 5 min). Use `cache=False` to bypass.
