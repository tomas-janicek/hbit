import typer

from hbit import bootstrap, endpoints, enums, settings

cli = typer.Typer()


@cli.command(name="get_agent_evaluation")
def get_agent_evaluation(question: str) -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.SQL_EXTRACTOR,
        patch_extractor_type=enums.PatchExtractorType.SQL_EXTRACTOR,
        device_evaluation_type=enums.DeviceEvaluationType.AI,
        patch_evaluation_type=enums.PatchEvaluationType.AI,
        summary_service_type=enums.SummaryServiceType.AI,
    )
    agent_evaluator = endpoints.AgentDeviceEvaluator(registry=registry)
    response = agent_evaluator.get_device_security_answer(question, print_steps=True)

    _print_response(response)


@cli.command(name="get_chain_evaluation")
def get_chain_evaluation(question: str) -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.STRUCTURED_EXTRACTOR,
        patch_extractor_type=enums.PatchExtractorType.STRUCTURED_EXTRACTOR,
        device_evaluation_type=enums.DeviceEvaluationType.IMPERATIVE,
        patch_evaluation_type=enums.PatchEvaluationType.IMPERATIVE,
        summary_service_type=enums.SummaryServiceType.AI,
    )
    chain_evaluator = endpoints.ChainDeviceEvaluator(registry=registry)
    response = chain_evaluator.get_device_security_answer(question, print_steps=True)

    _print_response(response)


@cli.command(name="get_structured_evaluation")
def get_structured_evaluation(question: str) -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.STRUCTURED_EXTRACTOR,
        patch_extractor_type=enums.PatchExtractorType.STRUCTURED_EXTRACTOR,
        device_evaluation_type=enums.DeviceEvaluationType.IMPERATIVE,
        patch_evaluation_type=enums.PatchEvaluationType.IMPERATIVE,
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
        device_evaluation_type=enums.DeviceEvaluationType.AI,
        patch_evaluation_type=enums.PatchEvaluationType.AI,
        summary_service_type=enums.SummaryServiceType.AI,
    )
    agent_evaluator = endpoints.ImperativeEvaluator(registry=registry)
    response = agent_evaluator.get_device_security_answer(question)

    _print_response(response)


@cli.command(name="save_graph_photos")
def save_graph_photos() -> None:
    registry = bootstrap.create_services(
        device_extractor_type=enums.DeviceExtractorType.SQL_EXTRACTOR,
        patch_extractor_type=enums.PatchExtractorType.SQL_EXTRACTOR,
        device_evaluation_type=enums.DeviceEvaluationType.AI,
        patch_evaluation_type=enums.PatchEvaluationType.AI,
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
