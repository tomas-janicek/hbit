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
    and get_patch_build! If device identifier or patch build is not correct, an error will
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
        return (
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
        return f"{detail} Try using other tools to get patch build in correct format."


@tool
def get_device_identifier(
    text: typing.Annotated[
        str, "User's text that may contain information about devices."
    ],
    config: RunnableConfig,
) -> str | None:
    """This tool requires input text from the user that mentions a device.
    - Before using this tool, ensure the user has provided details about their device.
    - If the user has not mentioned a device, ask them to specify which device they are referring to before proceeding.

    Use this tool only if:
    1. The user's question contains text about a device, but you cannot determine the device identifier.
    2. You need to extract the device identifier from the provided text.

    If no device identifier is found, prompt the user to provide more details about their device before retrying.
    Example text: How secure is an iPhone XS?
    Example output: iphone11,2"""
    registry = _get_registry_from_config(config)
    device_extractor = registry.get_service(extractors.DeviceExtractor)

    device_identifier = device_extractor.extract_device_identifier(text=text)

    if not device_identifier:
        return (
            "User did not provide valid or enough data to identify device. "
            "Ask user to provide more information about device."
        )

    return device_identifier


@tool
def get_patch_build(
    text: typing.Annotated[
        str, "User's text that may contain information about patches."
    ],
    config: RunnableConfig,
) -> str | None:
    """This tool requires input text from the user that mentions a patch.
    - Before using this tool, ensure the user has provided details about the patch installed on their device.
    - If the user has not mentioned a patch, ask them to specify which patch they are referring to before proceeding.

    Use this tool only if:
    1. The user's question contains text about a patch, but you cannot determine the patch build.
    2. You need to extract the patch build information from the provided text.

    If no patch build is found, prompt the user to provide more details about the patch installed on their device before retrying.
    Example text: How secure is my iPhone 13 Pro if I have patch 18.1.0 installed?
    Example output: 22b83"""
    registry = _get_registry_from_config(config)
    patch_extractor = registry.get_service(extractors.PatchExtractor)

    patch_build = patch_extractor.extract_patch_build(text=text)

    if not patch_build:
        return (
            "User did not provide valid or enough data to identify patch."
            "Ask user to provide more information about patch installed on his device."
        )

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


# TODO: Tools ideas:
# - get all patches infos to help user get his patch / info
# - how can I do the same for devices
# - give user info on specific cve and other similar entities
# - search engine to get the rest of the missing data
