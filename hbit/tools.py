import typing

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool  # type: ignore
from langchain_core.tools.base import BaseTool, InjectedToolCallId
from langgraph.prebuilt import InjectedState  # type: ignore
from langgraph.types import Command

from hbit import dto, evaluations, extractors, services, summaries


@tool(return_direct=True)
def generate_evaluation_summary(
    state: typing.Annotated[dto.AgentStateSchema, InjectedState],
    config: RunnableConfig,
) -> str:
    """Generate summary from evaluation."""
    registry = _get_registry_from_config(config)
    summary_service = registry.get_service(summaries.SummaryService)

    question = str(state["messages"][0].content)
    summary = summary_service.generate_summary(
        question=question, evaluation=state["device_evaluation"]
    )
    return summary


@tool
def get_device_evaluation(  # type: ignore
    device_identifier: typing.Annotated[
        str, "Unique identifier of the device in format similar to 'iphone14,2'"
    ],
    patch_build: typing.Annotated[
        str, "Unique build of the patch in format similar to '22B83'"
    ],
    tool_call_id: typing.Annotated[str, InjectedToolCallId],
    config: RunnableConfig,
) -> Command:  # type: ignore
    """Input to this tool strings device identifier and patch build. Be sure that the
    device identifier and patch build have valid formats by calling get_device_identifier
    and get_patch_build! If device identifier or patch build is not correct, an error will
    be returned. If so, try using one of get_device_identifier or get_patch_build again.
    If you successfully retrieved evaluation, generate it's summary using
    generate_evaluation_summary tool.
    Example device identifier: 'iphone7,2', 'iphone9,4', 'iphone17,3'.
    Example patch build: '22b83', '21g93', '20h240', '19h370', '19b74'."""
    registry = _get_registry_from_config(config)
    evaluation_service = registry.get_service(evaluations.EvaluationService)

    evaluation = evaluation_service.get_trimmed_evaluation(
        device_identifier, patch_build
    )

    return Command(
        update={
            "device_evaluation": evaluation,
            "messages": [
                ToolMessage(
                    "Successfully retrieved device evaluation.",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )  # type: ignore


@tool
def get_device_identifier(
    state: typing.Annotated[dto.QuestionStateSchema, InjectedState],
    config: RunnableConfig,
) -> str | None:
    """Get device identifier."""
    registry = _get_registry_from_config(config)
    device_extractor = registry.get_service(extractors.DeviceExtractor)

    question = str(state["messages"][0].content)
    device_identifier = device_extractor.extract_device_identifier(text=question)
    return device_identifier


@tool
def get_patch_build(
    state: typing.Annotated[dto.QuestionStateSchema, InjectedState],
    config: RunnableConfig,
) -> str | None:
    """Get patch build."""
    registry = _get_registry_from_config(config)
    patch_extractor = registry.get_service(extractors.PatchExtractor)

    question = str(state["messages"][0].content)
    patch_build = patch_extractor.extract_patch_build(text=question)
    return patch_build


TOOLS: list[BaseTool] = [
    generate_evaluation_summary,
    get_device_evaluation,
    get_device_identifier,
    get_patch_build,
]


def _get_registry_from_config(config: RunnableConfig) -> services.ServiceContainer:
    registry = config.get("configurable", {}).get("registry", None)
    if not registry:
        raise RuntimeError(
            "Error in tool / model configuration. Registry must be part of RunnableConfig!"
        )
    return registry
