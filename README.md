## 📦 Netcord 2.0.0 — The Async Discord OAuth2 Toolkit for FastAPI

> A complete rewrite. Cleaner. Smarter. Async-native.

---

### ✨ What's New

* **Full Asynchronous Support**: Built entirely on `httpx.AsyncClient` for non-blocking HTTP interactions.
* **Pydantic Models**: Structured responses using `pydantic` for type safety and validation.
* **OAuth2 Flow Simplified**: Easily exchange codes for tokens and retrieve user data.
* **Scope Management**: Support for `identify`, `email`, and `guilds` scopes.
* **CDN Helpers**: Generate direct URLs for avatars and icons with format detection (`.gif`/`.png`).
* **Custom Exceptions**: Clear and informative error handling built upon `fastapi.HTTPException`.

---

### 🔧 Configuration

Set up your credentials once:

```python
from netcord import Netcord

client = Netcord(
    client_id='your_client_id',
    client_secret='your_client_secret',
    redirect_uri='https://yourapp.com/callback',
    bot_token='your_bot_token'
)
```



Then, use the client to interact with Discord's API seamlessly.
---

### 🧩 Integration with FastAPI

Designed to work harmoniously with FastAPI:

* Use dependencies to inject authenticated users into your routes.
* Leverage custom exceptions for consistent error responses.

*Note: While direct FastAPI integrations are planned, the current version focuses on providing the core functionality. Future updates will enhance this integration further.*

---

### 🚀 Why Upgrade?

* **Modern Architecture**: Leveraging the latest Python features and libraries.
* **Improved Developer Experience**: Cleaner codebase and better documentation.
* **Enhanced Performance**: Asynchronous operations lead to better scalability.
