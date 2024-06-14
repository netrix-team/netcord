# Netcord
Package for authentication with Discord API

## Installing
```
pip install netcord
```

## Example
```py
# main.py

import uvicorn
from pydantic import BaseModel

from os import getenv
from netcord import Netcord

from fastapi import FastAPI, Request
from fastapi import HTTPException

app = FastAPI(title='Your Site')

CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')
netcord = Netcord(CLIENT_ID, CLIENT_SECRET)


class RequestData(BaseModel):
    code: str
    state: str


@app.get('/auth/login')
async def login(session_id: str):
    return {'url': netcord.generate_auth_url(session_id)}


@app.post('/auth/callback')
async def callback(session_id: str, data: RequestData):
    try:
        netcord.check_state(session_id, data.state)
        tokens = await netcord.get_access_token(data.code)

        user = await netcord.get_user(tokens.access_token)
        return {'user': user.dict()}
    
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


if __name__ == '__main__':
    uvicorn.run(app, reload=True, log_level=20)
```
