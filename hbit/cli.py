import typer
from langchain_core.globals import set_debug, set_llm_cache, set_verbose
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from hbit import clients, device_security, extractors, settings

# TODO: Create common module for hbit_data.requests
from hbit_data import requests

cli = typer.Typer()


@cli.command(name="get_agent_evaluation")
def get_agent_evaluation(question: str) -> None:
    model = ChatGroq(model="llama-3.3-70b-versatile")  # type: ignore
    # model = ChatGroq(model="llama3-8b-8192")  # type: ignore
    agent_evaluator = device_security.AgentDeviceEvaluator(model=model)
    response = agent_evaluator.get_device_security_answer(question)
    print(
        "================================== Response ==================================\n"
    )
    print(response)


@cli.command(name="get_chain_evaluation")
def get_chain_evaluation(question: str) -> None:
    # model = ChatGroq(model="llama-3.3-70b-versatile")  # type: ignore
    model = ChatGroq(model="llama3-8b-8192")  # type: ignore
    agent_evaluator = device_security.ChainDeviceEvaluator(model=model)
    response = agent_evaluator.get_device_security_answer(question)
    print(
        "================================== Response ==================================\n"
    )
    print(response)


@cli.command(name="test_device_extraction")
def test_device_extraction(text: str) -> None:
    device_extractor, prompt_template = extractors.create_device_extractor()
    prompt = prompt_template.invoke({"input": text})
    device = device_extractor.invoke(prompt)
    print(
        "================================== Response ==================================\n"
    )
    print(device.model_dump())


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


@cli.command(name="test")
def test() -> None:
    hbit_request = requests.HTTPXRequests(requests.create_hbit_api_client())
    hbit = clients.HBITClient(request=hbit_request, hbit_api_url=settings.HBIT_API_URL)
    device_evalation = hbit.get_device_evaluation("iphone14,2", "22a3354")
    if device_evalation:
        print(device_evalation.model_dump())
    else:
        print("No evaluation found.")


if __name__ == "__main__":
    cli()
