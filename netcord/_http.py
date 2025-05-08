from httpx import AsyncClient, Response, HTTPError

__all__ = (
    'HTTPClient',
)


class HTTPClient(AsyncClient):
    def __init__(self, base_url: str) -> None:
        self._client = AsyncClient(base_url=base_url, timeout=10.0)

    async def _request(self, method: str, url: str, **kwargs) -> Response:
        try:
            response = await self._client.request(method, url, **kwargs)
        except HTTPError as e:
            raise HTTPError(f'HTTP error occurred: {e}')
        except Exception as e:
            raise Exception(f'An error occurred: {e}')

        return response

    async def get(self, url: str, **kwargs) -> Response:
        return await self._request('GET', url, **kwargs)

    async def post(self, url: str, **kwargs) -> Response:
        return await self._request('POST', url, **kwargs)

    async def put(self, url: str, **kwargs) -> Response:
        return await self._request('PUT', url, **kwargs)

    async def delete(self, url: str, **kwargs) -> Response:
        return await self._request('DELETE', url, **kwargs)

    async def patch(self, url: str, **kwargs) -> Response:
        return await self._request('PATCH', url, **kwargs)

    async def close(self) -> None:
        await self._client.aclose()
