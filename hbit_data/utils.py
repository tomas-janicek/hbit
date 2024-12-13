import typing
from xml.etree import ElementTree as ET

from url_normalize import url_normalize  # type: ignore

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
