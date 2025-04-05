import polars as pl

from hbit import enums, settings
from hbit.corpus import datasets


def test_loading_real_dataset() -> None:
    dataset = datasets.SecurityDataset(settings.SECURITY_PAPERS_PATH)

    assert dataset.data is not None
    assert dataset.data.shape[1] == 2
    assert len(dataset.data) > 0


def test_required_categories() -> None:
    dataset = datasets.SecurityDataset(settings.SECURITY_PAPERS_PATH)

    available_categories = set(dataset.data["category"].unique())
    required_categories = {c.value for c in enums.SecurityPaperCategory}

    assert available_categories.intersection(required_categories) == required_categories


def test_one_paper_content() -> None:
    dataset = datasets.SecurityDataset(settings.SECURITY_PAPERS_PATH)

    paper = dataset.data.select(pl.first("text", "category"))
    assert paper is not None
    assert paper["category"].item() in enums.SecurityPaperCategory
    assert paper["text"].item() is not None
