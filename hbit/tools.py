import typing

import httpx
from langchain.schema import BaseMessage, HumanMessage
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool  # type: ignore
from langchain_core.tools.base import BaseTool, InjectedToolCallId
from langgraph.prebuilt import InjectedState  # type: ignore
from langgraph.types import Command

from hbit import dto, evaluations, extractors, services, summaries


@tool(return_direct=True)
def generate_evaluation_summary(
    state: typing.Annotated[dto.EvaluationStateSchema, InjectedState],
    config: RunnableConfig,
) -> str:
    """Generate summary from evaluation."""
    registry = _get_registry_from_config(config)
    summary_service = registry.get_service(summaries.SummaryService)

    user_inputs = _get_human_messages(state["messages"])
    evaluation = state.get("evaluation")

    if not evaluation:
        # TODO: Create specific error message when patch and device are wrong
        raise ValueError(
            "First call get_device_evaluation or get_patch_evaluation to get at least one "
            "successful evaluation."
        )

    summary = summary_service.generate_summary(
        text=user_inputs,
        evaluation=evaluation,
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
    """Input to this tool are device identifier and patch build strings. Be sure that the
    device identifier and patch build have valid formats by calling get_device_identifier
    and get_patch_build! If device identifier or patch build is not correct, an error will
    be returned. If so, try using one of get_device_identifier or get_patch_build again.
    If you successfully retrieved evaluation, generate it's summary using
    generate_evaluation_summary tool.
    Example device identifier: 'iphone7,2', 'iphone9,4', 'iphone17,3'.
    Example patch build: '22b83', '21g93', '20h240', '19h370', '19b74'."""
    registry = _get_registry_from_config(config)
    evaluation_service = registry.get_service(evaluations.DeviceEvaluationService)

    try:
        evaluation = evaluation_service.get_trimmed_evaluation(
            device_identifier, patch_build
        )
    except httpx.HTTPStatusError:
        raise ValueError(
            "Could not retrieve device evaluation. Either device_identifier or patch_build "
            "is invalid. Try using other tools to get device_identifier and patch_build in "
            "correct format."
        )

    return Command(
        update={
            "evaluation": evaluation,
            "messages": [
                ToolMessage(
                    "Successfully retrieved device evaluation.",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )  # type: ignore


@tool
def get_patch_evaluation(  # type: ignore
    patch_build: typing.Annotated[
        str, "Unique build of the patch in format similar to '22B83'"
    ],
    tool_call_id: typing.Annotated[str, InjectedToolCallId],
    config: RunnableConfig,
) -> Command:  # type: ignore
    """Input to this tool is patch build string. Be sure that the
    patch build have valid format by calling get_patch_build!
    If patch build is not correct, an error will
    be returned. If so, try using get_patch_build tool.
    If you successfully retrieved evaluation, generate it's summary using
    generate_evaluation_summary tool.
    Example patch build: '22b83', '21g93', '20h240', '19h370', '19b74'."""
    registry = _get_registry_from_config(config)
    evaluation_service = registry.get_service(evaluations.PatchEvaluationService)

    evaluation = evaluation_service.get_trimmed_evaluation(patch_build)

    return Command(
        update={
            "evaluation": evaluation,
            "messages": [
                ToolMessage(
                    "Successfully retrieved patch evaluation.",
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

    user_inputs = _get_human_messages(state["messages"])
    device_identifier = device_extractor.extract_device_identifier(text=user_inputs)

    if not device_identifier:
        raise ValueError(
            "User did not provide valid or enough data to identify device. "
            "Ask user to provide more information about device."
        )

    return device_identifier


@tool
def get_patch_build(
    state: typing.Annotated[dto.QuestionStateSchema, InjectedState],
    config: RunnableConfig,
) -> str | None:
    """Get patch build."""
    registry = _get_registry_from_config(config)
    patch_extractor = registry.get_service(extractors.PatchExtractor)

    user_inputs = _get_human_messages(state["messages"])
    patch_build = patch_extractor.extract_patch_build(text=user_inputs)

    if not patch_build:
        raise ValueError("User did not provide valid or enough data to identify patch.")

    return patch_build


TOOLS: list[BaseTool] = [
    generate_evaluation_summary,
    get_device_evaluation,
    get_patch_evaluation,
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


def _get_human_messages(messages: typing.Sequence[BaseMessage]) -> str:
    human_texts: list[str] = []
    for message in messages:
        match message:
            case HumanMessage():
                human_texts.append(str(message.content))
            case _:
                pass
    return "\n".join(human_texts)
