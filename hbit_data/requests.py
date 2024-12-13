import logging
import typing

import httpx
import pydantic
import stamina
from authlib.integrations.httpx_client import OAuth2Client  # type: ignore

from hbit_data import settings, utils

_log = logging.getLogger(__name__)


ResponseT = typing.TypeVar("ResponseT")


class Requests:
    def get(
        self,
        *,
        base: str,
        path: str,
        response_type: type[ResponseT],
        params: dict[str, typing.Any] | None = None,
        timeout: int = settings.DEFAULT_TIMEOUT,
    ) -> ResponseT | None: ...

    def post(
        self,
        *,
        base: str,
        path: str,
        content: bytes,
        timeout: int = settings.DEFAULT_TIMEOUT,
    ) -> None: ...


class HTTPXRequests(Requests):
    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    @stamina.retry(
        on=httpx.HTTPError, attempts=3, wait_initial=5, wait_max=60, wait_exp_base=2
    )
    def get(
        self,
        *,
        base: str,
        path: str,
        response_type: type[ResponseT],
        params: dict[str, typing.Any] | None = None,
        timeout: int = settings.DEFAULT_TIMEOUT,
    ) -> ResponseT | None:
        url = utils.create_url(base, path)
        try:
            response = self.client.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            type_adapter = pydantic.TypeAdapter[response_type](response_type)
            response_data = type_adapter.validate_json(response.content)
            return response_data
        except httpx.RequestError as exc:
            _log.error("An error occurred while requesting %s.", exc.request.url)
        except httpx.HTTPStatusError as exc:
            _log.error(
                "Error response %s while requesting %s.",
                exc.response.status_code,
                exc.request.url,
            )
            raise exc

    @stamina.retry(
        on=httpx.HTTPError, attempts=3, wait_initial=5, wait_max=60, wait_exp_base=2
    )
    def post(
        self,
        *,
        base: str,
        path: str,
        content: bytes,
        timeout: int = settings.DEFAULT_TIMEOUT,
    ) -> None:
        url = utils.create_url(base, path)
        try:
            response = self.client.post(url, content=content, timeout=timeout)
            response.raise_for_status()
        except httpx.RequestError as exc:
            _log.error("An error occurred while requesting %s.", exc.request.url)
        except httpx.HTTPStatusError as exc:
            _log.error(
                "Error response %s while requesting %s.",
                exc.response.status_code,
                exc.request.url,
            )
            raise exc


def create_hbit_api_client() -> httpx.Client:
    client = OAuth2Client()

    token_endpoint = utils.create_url(
        base=settings.HBIT_API_URL, path="/login/access-token"
    )
    client.fetch_token(
        token_endpoint,
        username=settings.ADMIN_EMAIL,
        password=settings.ADMIN_PASSWORD,
    )
    return client
