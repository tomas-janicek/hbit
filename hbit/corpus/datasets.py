import logging
import typing
from pathlib import Path

import polars as pl
from langchain.schema import Document
from langchain_core.document_loaders import BaseLoader
from langdetect import detect  # type: ignore

from hbit import dto, enums

_log = logging.getLogger(__name__)


class SecurityDataset:
    def __init__(self, path: Path) -> None:
        self.path = path

    def get_english_paper(
        self, length: int | None = None
    ) -> typing.Iterator[dto.SecurityPaper]:
        self.data = pl.read_parquet(self.path)
        _log.info(f"Dataset loaded from {self.path} with length {len(self.data)}.")
        returned_rows = 0
        for row in self.data.iter_rows(named=True):
            text = row["text"]
            if detect(text) == "en":
                returned_rows += 1
                yield dto.SecurityPaper(
                    text=text, category=enums.SecurityPaperCategory(row["category"])
                )
            if length and returned_rows >= length:
                break

    @staticmethod
    def save_dataset(hf_location: str, path: Path) -> None:
        data = pl.read_parquet(hf_location)
        data.write_parquet(path)
        _log.info(f"Dataset saved to {path} with length {len(data)}.")


class SecurityPaperLoader(BaseLoader):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.dataset = SecurityDataset(path)

    def lazy_load(self) -> typing.Iterator[Document]:
        for paper in self.dataset.get_english_paper():
            yield Document(
                page_content=paper.text,
                metadata={"category": paper.category, "source": str(self.path)},
            )
