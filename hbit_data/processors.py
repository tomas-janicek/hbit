import typing

from hbit_data import scrapers, utils

ItemT = typing.TypeVar("ItemT")


class Pipeline(typing.Protocol, typing.Generic[ItemT]):
    def process_batch(self, items: list[ItemT]) -> None: ...

    def end_processing(self) -> None: ...


class ItemProcessor(typing.Generic[ItemT]):
    def __init__(self, batch_size: int, pipelines: list[Pipeline[ItemT]]) -> None:
        self.batch_size = batch_size
        self.pipelines = pipelines

    def process(self, scraper: scrapers.Scraper[ItemT]) -> None:
        scraped_items_it = scraper.scrape()
        batched_items_it = utils.batched_iterator(scraped_items_it, self.batch_size)
        for batch in batched_items_it:
            self.process_batch(batch)

        self.end_processing()

    def process_batch(self, items: list[ItemT]) -> None:
        for pipeline in self.pipelines:
            pipeline.process_batch(items)

    def end_processing(self) -> None:
        for pipeline in self.pipelines:
            pipeline.end_processing()
