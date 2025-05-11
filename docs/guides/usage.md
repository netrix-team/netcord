# 🔧 Usage

A simple FastAPI integration example.

---

## 1. Initialize Netcord

```python
from fastapi import FastAPI
from netcord import Netcord

app = FastAPI()

netcord = Netcord(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_SECRET',
    redirect_uri='https://yourapp.com/callback',
    scopes=('identify', 'email'),
    bot_token='YOUR_BOT_TOKEN'  # optional, for some endpoints
)
```

## 2. Redirect user to Discord

```python
from fastapi.responses import RedirectResponse

@app.get('/login')
async def login():
    url = netcord.generate_auth_url(state='random_state')
    return RedirectResponse(url)
```

## 3. Handle callback & exchange code

```python
from fastapi import Request

@app.get('/callback')
async def callback(request: Request):
    code = request.query_params.get('code')
    token = await netcord.exchange_code(code)
    return {'token': token.to_dict()}
```

## 4. Fetch user & guilds

```python
@app.get('/me')
async def me(token: str):
    user = await netcord.fetch_user(token)
    guilds = await netcord.fetch_guilds(token)
    return {
        'user': user.to_dict(),
        'guilds': [g.to_dict() for g in guilds]
    }
```

!!! Tip
    Netcord caches fetch_user & fetch_guilds for 5 minutes by default. Use cache=False to bypass.
