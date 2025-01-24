import typer

from hbit import bootstrap, core, endpoints, enums, models, settings
from hbit.extractors import device_extractors, patch_extractors

cli = typer.Typer()


@cli.command(name="get_agent_evaluation")
def get_agent_evaluation(question: str) -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.SQL_EXTRACTOR,
        patch_extractor_type=enums.PatchExtractorType.SQL_EXTRACTOR,
        evaluation_service_type=enums.EvaluationServiceType.AI,
        summary_service_type=enums.SummaryServiceType.AI,
    )
    agent_evaluator = endpoints.AgentDeviceEvaluator(registry=registry)
    response = agent_evaluator.get_device_security_answer(question)

    _print_response(response)


@cli.command(name="get_chain_evaluation")
def get_chain_evaluation(question: str) -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.STRUCTURED_EXTRACTOR,
        patch_extractor_type=enums.PatchExtractorType.STRUCTURED_EXTRACTOR,
        evaluation_service_type=enums.EvaluationServiceType.IMPERATIVE,
        summary_service_type=enums.SummaryServiceType.AI,
    )
    chain_evaluator = endpoints.ChainDeviceEvaluator(registry=registry)
    response = chain_evaluator.get_device_security_answer(question)

    _print_response(response)


@cli.command(name="get_structured_evaluation")
def get_structured_evaluation(question: str) -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.STRUCTURED_EXTRACTOR,
        patch_extractor_type=enums.PatchExtractorType.STRUCTURED_EXTRACTOR,
        evaluation_service_type=enums.EvaluationServiceType.IMPERATIVE,
        summary_service_type=enums.SummaryServiceType.AI,
    )
    agent_evaluator = endpoints.ImperativeEvaluator(registry=registry)
    response = agent_evaluator.get_device_security_answer(question)

    _print_response(response)


@cli.command(name="get_sql_evaluation")
def get_sql_evaluation(question: str) -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.SQL_EXTRACTOR,
        patch_extractor_type=enums.PatchExtractorType.SQL_EXTRACTOR,
        evaluation_service_type=enums.EvaluationServiceType.AI,
        summary_service_type=enums.SummaryServiceType.AI,
    )
    agent_evaluator = endpoints.ImperativeEvaluator(registry=registry)
    response = agent_evaluator.get_device_security_answer(question)

    _print_response(response)


# TODO: Create notebook for this tests


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


@cli.command(name="save_graph_photos")
def save_graph_photos() -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.SQL_EXTRACTOR,
        patch_extractor_type=enums.PatchExtractorType.SQL_EXTRACTOR,
        evaluation_service_type=enums.EvaluationServiceType.AI,
        summary_service_type=enums.SummaryServiceType.AI,
    )
    agent_evaluator = endpoints.ChainDeviceEvaluator(registry=registry)
    agent_evaluator.save_graph_image(settings.STATIC_DIR / "chain-graph.png")


def _print_response(response: str) -> None:
    print(
        "================================== Response ==================================\n"
    )
    print(response)


if __name__ == "__main__":
    cli()
