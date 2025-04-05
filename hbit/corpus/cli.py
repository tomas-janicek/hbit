import json

import typer

from hbit import bootstrap, core, dto, enums, settings
from hbit.corpus import datasets, vector_services

# pretty_exceptions must be disabled because it doesn't work with MilvusException
cli = typer.Typer(pretty_exceptions_enable=False)


@cli.command(name="load_security_papers_dataset")
def load_security_papers_dataset(length: int = 1) -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.SQL,
        patch_extractor_type=enums.PatchExtractorType.SQL,
        summary_service_type=enums.SummaryServiceType.AI,
        model_provider=enums.ModelProvider.OPEN_AI,
    )

    security_papers = vector_services.SecurityPapersService(registry)

    dataset = datasets.SecurityDataset(settings.SECURITY_PAPERS_PATH)
    security_papers.save_texts(dataset.get_english_paper(length))


@cli.command(name="search_vector_db")
def search_vector_db(
    query: str, category: enums.SecurityPaperCategory | None = None, n_results: int = 5
) -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.SQL,
        patch_extractor_type=enums.PatchExtractorType.SQL,
        summary_service_type=enums.SummaryServiceType.AI,
        model_provider=enums.ModelProvider.OPEN_AI,
    )

    security_papers = vector_services.SecurityPapersService(registry)
    results = security_papers.query_vector_db(
        query=query,
        query_filters=dto.SecurityPaperQuery(category=category),
        n_results=n_results,
    )

    _print_responses([str(paper) for paper in results])


@cli.command(name="get_collection_info")
def get_collection_info() -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.SQL,
        patch_extractor_type=enums.PatchExtractorType.SQL,
        summary_service_type=enums.SummaryServiceType.AI,
        model_provider=enums.ModelProvider.OPEN_AI,
    )

    security_papers = vector_services.SecurityPapersService(registry)
    collection_info = security_papers.get_collection_info()

    print(
        "================================== Collection Info ==================================\n"
    )
    print(json.dumps(collection_info, indent=4, sort_keys=True))


@cli.command(name="save_security_papers_dataset")
def save_security_papers_dataset() -> None:
    datasets.SecurityDataset.save_dataset(
        hf_location=settings.SECURITY_PAPERS_HF_LOCATION,
        path=settings.SECURITY_PAPERS_PATH,
    )


@cli.command(name="create_db")
def create_db() -> None:
    db = core.VectorService()
    db.create_database(settings.VECTOR_DB_NAME)


@cli.command(name="create_security_papers")
def create_security_papers(re_create: bool = False) -> None:
    db = core.VectorService()
    if re_create:
        db.re_create_security_papers()
    else:
        db.create_security_papers()


def _print_responses(responses: list[str]) -> None:
    for i, response in enumerate(responses):
        print(
            f"================================== Response {i + 1} ==================================\n"
        )
        print(response)


if __name__ == "__main__":
    cli()
