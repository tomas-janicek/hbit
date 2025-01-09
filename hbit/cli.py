import typer
from langchain_core.globals import set_debug, set_llm_cache, set_verbose
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from common import requests
from hbit import clients, device_security, evaluations, settings, utils
from hbit.extractors import device_extractors, patch_extractors

cli = typer.Typer()


@cli.command(name="get_agent_evaluation")
def get_agent_evaluation(question: str) -> None:
    model = ChatGroq(model="llama-3.3-70b-versatile")  # type: ignore
    agent_evaluator = device_security.AgentDeviceEvaluator(model=model)
    response = agent_evaluator.get_device_security_answer(question)
    print(
        "================================== Response ==================================\n"
    )
    print(response)


@cli.command(name="get_chain_evaluation")
def get_chain_evaluation(question: str) -> None:
    model = ChatGroq(model="llama-3.3-70b-versatile")  # type: ignore
    agent_evaluator = device_security.ChainDeviceEvaluator(model=model)
    response = agent_evaluator.get_device_security_answer(question)
    print(
        "================================== Response ==================================\n"
    )
    print(response)


@cli.command(name="get_structured_evaluation")
def get_structured_evaluation(question: str) -> None:
    model = ChatGroq(model="llama-3.3-70b-versatile")  # type: ignore
    request = requests.HTTPXRequests(utils.create_hbit_api_client())
    client = clients.ApiHBITClient(request, settings.HBIT_API_URL)
    device_extractor = device_extractors.StructureDeviceExtractor(model)
    patch_extractor = patch_extractors.SqlPatchExtractor(model)
    evaluation_service = evaluations.IterativeEvaluationService(client)
    agent_evaluator = device_security.SummarizationEvaluator(
        model=model,
        device_extractor=device_extractor,
        evaluation_service=evaluation_service,
        patch_extractor=patch_extractor,
    )
    response = agent_evaluator.get_device_security_answer(question)
    print(
        "================================== Response ==================================\n"
    )
    print(response)


@cli.command(name="get_sql_evaluation")
def get_sql_evaluation(question: str) -> None:
    model = ChatGroq(model="llama-3.3-70b-versatile")  # type: ignore
    request = requests.HTTPXRequests(utils.create_hbit_api_client())
    client = clients.ApiHBITClient(request, settings.HBIT_API_URL)
    device_extractor = device_extractors.SqlDeviceExtractor(model)
    patch_extractor = patch_extractors.SqlPatchExtractor(model)
    evaluation_service = evaluations.AiEvaluationService(
        model, client, n_vulnerabilities=10
    )
    agent_evaluator = device_security.SummarizationEvaluator(
        model=model,
        device_extractor=device_extractor,
        patch_extractor=patch_extractor,
        evaluation_service=evaluation_service,
    )
    response = agent_evaluator.get_device_security_answer(question)
    print(
        "================================== Response ==================================\n"
    )
    print(response)


@cli.command(name="translate_text_to")
def translate_text_to(language: str, text: str, debug: bool = False) -> None:
    set_verbose(True)
    set_debug(debug)
    set_llm_cache(None)

    model = ChatGroq(model="llama3-8b-8192")  # type: ignore

    system_template = "Translate the following from English into {language}"

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{text}")]
    )
    prompt = prompt_template.invoke({"language": language, "text": text})

    response = model.invoke(prompt)
    print(response.content)


@cli.command(name="test_device_extraction")
def test_structured_device_extraction(text: str) -> None:
    model = ChatGroq(model="llama-3.3-70b-versatile")  # type: ignore
    device_extractor = device_extractors.StructureDeviceExtractor(model)
    identifier = device_extractor.extract_device_identifier(text)
    print(
        "================================== Response ==================================\n"
    )
    print(f"Extracted device identifier: {identifier}")


@cli.command(name="test_sql_device_extractor")
def test_sql_device_extractor(text: str) -> None:
    model = ChatGroq(model="llama-3.3-70b-versatile")  # type: ignore
    device_extractor = device_extractors.SqlDeviceExtractor(model)
    identifier = device_extractor.extract_device_identifier(text)
    print(
        "================================== Response ==================================\n"
    )
    print(f"Extracted device identifier: {identifier}")


@cli.command(name="test_patch_extraction")
def test_structured_patch_extraction(text: str) -> None:
    model = ChatGroq(model="llama-3.3-70b-versatile")  # type: ignore
    patch_extractor = patch_extractors.StructurePatchExtractor(model)
    build = patch_extractor.extract_patch_build(text)
    print(
        "================================== Response ==================================\n"
    )
    print(f"Extracted patch build: {build}")


@cli.command(name="test_sql_patch_extractor")
def test_sql_patch_extractor(text: str) -> None:
    model = ChatGroq(model="llama-3.3-70b-versatile")  # type: ignore
    patch_extractor = patch_extractors.SqlPatchExtractor(model)
    build = patch_extractor.extract_patch_build(text)
    print(
        "================================== Response ==================================\n"
    )
    print(f"Extracted patch build: {build}")


@cli.command(name="get_device_vulnerabilities")
def get_device_vulnerabilities() -> None:
    hbit_request = requests.HTTPXRequests(utils.create_hbit_api_client())
    hbit = clients.ApiHBITClient(
        request=hbit_request, hbit_api_url=settings.HBIT_API_URL
    )
    device_evalation = hbit.get_device_evaluation("iphone14,2", "22a3354")
    if device_evalation:
        print(device_evalation.model_dump())
    else:
        print("No evaluation found.")


if __name__ == "__main__":
    cli()
