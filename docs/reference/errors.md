# 🚨 Errors

Custom HTTPException subclasses.

---

## `class NetError(HTTPException): ...`
Base Exception

## `class AuthenticationError(NetError): ...`
Returns 401 if authentication is incorrect

## `class TokenExchangeError(NetError): ...`
Returns 400 if the authentication code exchange failed
