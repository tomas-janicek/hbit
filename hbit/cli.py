import typer
from langchain_core.rate_limiters import InMemoryRateLimiter

from common import requests
from hbit import (
    clients,
    core,
    device_security,
    evaluations,
    models,
    settings,
    summaries,
    utils,
)
from hbit.extractors import device_extractors, patch_extractors

cli = typer.Typer()

model_name = "llama3-70b-8192"
rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.075,  # one request in 4 seconds
    check_every_n_seconds=0.5,
    max_bucket_size=1,
)


@cli.command(name="get_agent_evaluation")
def get_agent_evaluation(question: str) -> None:
    db = core.DatabaseService()
    agent_evaluator = device_security.AgentDeviceEvaluator(
        model=models.default_model, db=db
    )
    response = agent_evaluator.get_device_security_answer(question)

    _print_response(response)


@cli.command(name="get_chain_evaluation")
def get_chain_evaluation(question: str) -> None:
    db = core.DatabaseService()
    request = requests.HTTPXRequests(utils.create_hbit_api_client())
    client = clients.ApiHBITClient(request, settings.HBIT_API_URL)
    device_extractor = device_extractors.StructureDeviceExtractor(
        model=models.default_model, db=db
    )
    patch_extractor = patch_extractors.StructurePatchExtractor(
        model=models.default_model, db=db
    )
    evaluation_service = evaluations.IterativeEvaluationService(client)
    summary_service = summaries.AiSummaryService(
        summary_model=models.smaller_model, analysis_model=models.default_model
    )
    agent_evaluator = device_security.ChainDeviceEvaluator(
        model=models.default_model,
        summary_service=summary_service,
        device_extractor=device_extractor,
        evaluation_service=evaluation_service,
        patch_extractor=patch_extractor,
    )
    response = agent_evaluator.get_device_security_answer(question)

    _print_response(response)


@cli.command(name="get_structured_evaluation")
def get_structured_evaluation(question: str) -> None:
    db = core.DatabaseService()
    request = requests.HTTPXRequests(utils.create_hbit_api_client())
    client = clients.ApiHBITClient(request, settings.HBIT_API_URL)
    device_extractor = device_extractors.StructureDeviceExtractor(
        model=models.default_model, db=db
    )
    patch_extractor = patch_extractors.StructurePatchExtractor(
        model=models.default_model, db=db
    )
    evaluation_service = evaluations.IterativeEvaluationService(client)
    summary_service = summaries.AiSummaryService(
        summary_model=models.smaller_model, analysis_model=models.default_model
    )
    agent_evaluator = device_security.SummarizationEvaluator(
        model=models.default_model,
        summary_service=summary_service,
        device_extractor=device_extractor,
        evaluation_service=evaluation_service,
        patch_extractor=patch_extractor,
    )
    response = agent_evaluator.get_device_security_answer(question)

    _print_response(response)


@cli.command(name="get_sql_evaluation")
def get_sql_evaluation(question: str) -> None:
    db = core.DatabaseService()
    request = requests.HTTPXRequests(utils.create_hbit_api_client())
    client = clients.ApiHBITClient(request, settings.HBIT_API_URL)
    device_extractor = device_extractors.SqlDeviceExtractor(
        model=models.default_model, db=db
    )
    patch_extractor = patch_extractors.SqlPatchExtractor(
        model=models.default_model, db=db
    )
    evaluation_service = evaluations.IterativeEvaluationService(client=client)
    summary_service = summaries.AiSummaryService(
        summary_model=models.smaller_model, analysis_model=models.default_model
    )
    agent_evaluator = device_security.SummarizationEvaluator(
        model=models.default_model,
        summary_service=summary_service,
        device_extractor=device_extractor,
        patch_extractor=patch_extractor,
        evaluation_service=evaluation_service,
    )
    response = agent_evaluator.get_device_security_answer(question)

    _print_response(response)


@cli.command(name="test_device_extraction")
def test_structured_device_extraction(text: str) -> None:
    db = core.DatabaseService()
    device_extractor = device_extractors.StructureDeviceExtractor(
        model=models.code_model, db=db
    )
    identifier = device_extractor.extract_device_identifier(text)

    _print_response(f"Extracted device identifier: {identifier}")


@cli.command(name="test_sql_device_extractor")
def test_sql_device_extractor(text: str) -> None:
    db = core.DatabaseService()
    device_extractor = device_extractors.SqlDeviceExtractor(
        model=models.code_model, db=db
    )
    identifier = device_extractor.extract_device_identifier(text)

    _print_response(f"Extracted device identifier: {identifier}")


@cli.command(name="test_patch_extraction")
def test_structured_patch_extraction(text: str) -> None:
    db = core.DatabaseService()
    patch_extractor = patch_extractors.StructurePatchExtractor(
        model=models.code_model, db=db
    )
    build = patch_extractor.extract_patch_build(text)

    _print_response(f"Extracted patch build: {build}")


@cli.command(name="test_sql_patch_extractor")
def test_sql_patch_extractor(text: str) -> None:
    db = core.DatabaseService()
    patch_extractor = patch_extractors.SqlPatchExtractor(model=models.code_model, db=db)
    build = patch_extractor.extract_patch_build(text)

    _print_response(f"Extracted patch build: {build}")


def _print_response(response: str) -> None:
    print(
        "================================== Response ==================================\n"
    )
    print(response)


if __name__ == "__main__":
    cli()
