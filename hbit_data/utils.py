import typing
from itertools import islice
from xml.etree import ElementTree as ET

import httpx
from authlib.integrations.httpx_client import OAuth2Client  # type: ignore
from url_normalize import url_normalize  # type: ignore

from common import utils
from hbit_data import settings

ItemT = typing.TypeVar("ItemT")


def get_all_text(element: ET.Element | None) -> str:
    texts: list[str] = []
    if element is None:
        return ""
    if element.text:
        texts.append(element.text.strip())
    texts.extend(get_all_text(e) for e in element)
    if element.tail:
        texts.append(element.tail.strip())
    return " ".join(filter(None, texts))


def create_url(base: str, path: str) -> str:
    url = f"{base}/{path}"
    return url_normalize(url)  # type: ignore


def batched_iterator(
    iterable: typing.Iterable[ItemT], batch_size: int
) -> typing.Iterator[list[ItemT]]:
    iterator = iter(iterable)  # Create an iterator from the iterable
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            break
        yield batch


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
