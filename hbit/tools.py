import typing

import httpx
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool  # type: ignore
from langchain_core.tools.base import BaseTool

from hbit import evaluations, extractors, services, summaries


@tool
def get_device_evaluation(
    device_identifier: typing.Annotated[
        str, "Unique identifier of the device in format similar to 'iphone14,2'"
    ],
    patch_build: typing.Annotated[
        str, "Unique build of the patch in format similar to '22B83'"
    ],
    config: RunnableConfig,
) -> str:
    """Input to this tool are device identifier and patch build strings. Be sure that the
    device identifier and patch build have valid formats by calling get_device_identifier
    and get_patch_build! If device identifier or patch build is not correct,
    -an error will
    be returned. If so, try using one of get_device_identifier or get_patch_build again.
    If you successfully retrieved evaluation, generate it's summary using
    generate_evaluation_summary tool.
    Example device identifier: 'iphone7,2', 'iphone9,4', 'iphone17,3'.
    Example patch build: '22b83', '21g93', '20h240', '19h370', '19b74'."""
    registry = _get_registry_from_config(config)
    evaluation_service = registry.get_service(evaluations.DeviceEvaluationService)
    summary_service = registry.get_service(summaries.SummaryService)

    try:
        evaluation = evaluation_service.get_full_evaluation(
            device_identifier, patch_build
        )
        summary = summary_service.generate_summary(evaluation=evaluation)
        return summary
    except httpx.HTTPStatusError as error:
        detail = error.response.json().get("detail", "")
        raise ValueError(
            f"{detail}"
            "Try using other tools to get device identifier or patch build in "
            "correct format."
        )


@tool
def get_patch_evaluation(
    patch_build: typing.Annotated[
        str, "Unique build of the patch in format similar to '22B83'"
    ],
    config: RunnableConfig,
) -> str:
    """Input to this tool is patch build string. Be sure that the
    patch build have valid format by calling get_patch_build!
    If patch build is not correct, an error will
    be returned. If so, try using get_patch_build tool.
    If you successfully retrieved evaluation, generate it's summary using
    generate_evaluation_summary tool.
    Example patch build: '22b83', '21g93', '20h240', '19h370', '19b74'."""
    registry = _get_registry_from_config(config)
    evaluation_service = registry.get_service(evaluations.PatchEvaluationService)
    summary_service = registry.get_service(summaries.SummaryService)

    try:
        evaluation = evaluation_service.get_full_evaluation(patch_build)
        summary = summary_service.generate_summary(evaluation=evaluation)
        return summary
    except httpx.HTTPStatusError as error:
        detail = error.response.json().get("detail", "")
        raise ValueError(
            f"{detail} Try using other tools to get patch build in correct format."
        )


# TODO: Can I somehow use both SQL and JSON extractors
@tool
def get_device_identifier(
    text: typing.Annotated[
        str, "Human text that may contain information about devices."
    ],
    config: RunnableConfig,
) -> str | None:
    """Get device identifier.
    The input should contain ONLY text provided by user."""
    registry = _get_registry_from_config(config)
    device_extractor = registry.get_service(extractors.DeviceExtractor)

    device_identifier = device_extractor.extract_device_identifier(text=text)

    if not device_identifier:
        raise ValueError(
            "User did not provide valid or enough data to identify device. "
            "Ask user to provide more information about device."
        )

    return device_identifier


@tool
def get_patch_build(
    text: typing.Annotated[
        str, "Human text that may contain information about devices."
    ],
    config: RunnableConfig,
) -> str | None:
    """Get patch build.
    The input should contain ONLY text provided by user."""
    registry = _get_registry_from_config(config)
    patch_extractor = registry.get_service(extractors.PatchExtractor)

    patch_build = patch_extractor.extract_patch_build(text=text)

    if not patch_build:
        raise ValueError("User did not provide valid or enough data to identify patch.")

    return patch_build


TOOLS: list[BaseTool] = [
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
