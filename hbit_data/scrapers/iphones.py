from collections.abc import Iterator

from hbit_data import dto

from . import base


class iPhoneScraper(base.Scraper[dto.iPhone]):
    def scrape(self) -> Iterator[dto.iPhone]: ...
