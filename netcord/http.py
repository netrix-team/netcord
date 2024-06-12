from aiohttp import ClientSession, BasicAuth
from aiohttp import ClientResponseError, ClientTimeout

from netcord.logger import get_logger
logger = get_logger(__name__)


class HTTPClient:
    def __init__(self, timeout: int = 20) -> None:
        self.timeout = ClientTimeout(timeout)

    async def fetch(self, method: str, url: str, headers: dict,
        data: dict = None, auth: BasicAuth = None, return_class=None):

        try:
            async with ClientSession(timeout=self.timeout) as session:
                async with session.request(method=method, url=url,
                    headers=headers, data=data, auth=auth) as response:

                    response.raise_for_status()
                    result = await response.json(encoding='utf-8')

                    logger.info(f'Success: {response.status}; '
                                f'{response.method} -> {response.url}')

                    if result is None:
                        return

                    if return_class:
                        if isinstance(result, list):
                            return [return_class(**item) for item in result]

                        return return_class(**result)

                    return result

        except ClientResponseError as error:
            logger.error(
                f'ClientError: {error.status} - {error.message}; '
                f'{error.request_info.method} -> {error.request_info.url}')
            return

        except Exception as exc:
            logger.error(f'Unknown error: {exc}')
            return
