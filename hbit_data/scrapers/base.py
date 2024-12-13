import typing

ItemT = typing.TypeVar("ItemT")


class Scraper(typing.Protocol, typing.Generic[ItemT]):  # type: ignore
    def scrape(self) -> typing.Iterator[ItemT]: ...
