import logging
import typing

import httpx
import pydantic
import stamina

from common import utils

_log = logging.getLogger(__name__)


ResponseT = typing.TypeVar("ResponseT")


class Requests:
    def get_or_retry(
        self,
        *,
        base: str,
        path: str,
        response_type: type[ResponseT],
        timeout: int,
        params: dict[str, typing.Any] | None = None,
    ) -> ResponseT: ...

    def get(
        self,
        *,
        base: str,
        path: str,
        response_type: type[ResponseT],
        timeout: int,
        params: dict[str, typing.Any] | None = None,
    ) -> ResponseT: ...

    def post_or_retry(
        self,
        *,
        base: str,
        path: str,
        content: bytes,
        timeout: int,
        params: dict[str, typing.Any] | None = None,
    ) -> None: ...

    def post(
        self,
        *,
        base: str,
        path: str,
        content: bytes,
        timeout: int,
        params: dict[str, typing.Any] | None = None,
    ) -> None: ...


class HTTPXRequests(Requests):
    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    @stamina.retry(
        on=httpx.HTTPStatusError,
        attempts=3,
        wait_initial=5,
        wait_max=60,
        wait_exp_base=2,
    )
    def get_or_retry(
        self,
        *,
        base: str,
        path: str,
        response_type: type[ResponseT],
        timeout: int,
        params: dict[str, typing.Any] | None = None,
    ) -> ResponseT:
        return self.get(
            base=base,
            path=path,
            response_type=response_type,
            timeout=timeout,
            params=params,
        )

    def get(
        self,
        *,
        base: str,
        path: str,
        response_type: type[ResponseT],
        timeout: int,
        params: dict[str, typing.Any] | None = None,
    ) -> ResponseT:
        url = utils.create_url(base, path)
        try:
            response = self.client.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            type_adapter = pydantic.TypeAdapter[response_type](response_type)
            response_data = type_adapter.validate_json(response.content)
            return response_data
        except httpx.RequestError as exc:
            _log.error("An error occurred while requesting %s.", exc.request.url)
            raise exc
        except httpx.HTTPStatusError as exc:
            _log.error(
                "Error response %s while requesting %s.",
                exc.response.status_code,
                exc.request.url,
            )
            raise exc

    @stamina.retry(
        on=httpx.HTTPStatusError,
        attempts=3,
        wait_initial=5,
        wait_max=60,
        wait_exp_base=2,
    )
    def post_or_retry(
        self,
        *,
        base: str,
        path: str,
        content: bytes,
        timeout: int,
        params: dict[str, typing.Any] | None = None,
    ) -> None:
        return self.post(
            base=base,
            path=path,
            content=content,
            timeout=timeout,
            params=params,
        )

    def post(
        self,
        *,
        base: str,
        path: str,
        content: bytes,
        timeout: int,
        params: dict[str, typing.Any] | None = None,
    ) -> None:
        url = utils.create_url(base, path)
        try:
            response = self.client.post(
                url, params=params, content=content, timeout=timeout
            )
            response.raise_for_status()
        except httpx.RequestError as exc:
            _log.error("An error occurred while requesting %s.", exc.request.url)
            raise exc
        except httpx.HTTPStatusError as exc:
            _log.error(
                "Error response %s while requesting %s.",
                exc.response.status_code,
                exc.request.url,
            )
            raise exc
