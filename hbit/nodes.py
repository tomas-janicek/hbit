import typing

from langchain.schema import AIMessage
from langchain_core.runnables import RunnableConfig

from hbit import clients, dto, enums, extractors, settings, summaries, types, utils


def reset_max_steps(state: dto.GraphStateSchema) -> dict[str, typing.Any]:
    return {"max_steps": settings.MAX_STEPS, "current_step": 0}


def respond_to_user(
    state: dto.GraphStateSchema, config: RunnableConfig
) -> dict[str, typing.Any]:
    registry = utils.get_registry_from_config(config)
    model = registry.get_service(types.AgentModel)
    response = model.invoke(state["messages"])
    return {"messages": response}


def get_device_evaluation(
    state: dto.DeviceEvaluationSchema, config: RunnableConfig
) -> dict[str, typing.Any]:
    """Get the evaluation of a device."""
    registry = utils.get_registry_from_config(config)
    client = registry.get_service(clients.HBITClient)
    summary_service = registry.get_service(summaries.SummaryService)

    try:
        evaluation = client.get_device_evaluation(
            device_identifier=state["device_identifier"],
            patch_build=state["patch_build"],
        )
        summary = summary_service.generate_summary(evaluation)
        message = AIMessage(
            f"Success: Action {enums.GraphAction.DEVICE_EVALUATION} created evaluation:\n{summary}"
        )
        return {"messages": message}
    except Exception as error:
        message = AIMessage(f"Error occurred: {error}")
        return {"messages": message}


def get_patch_evaluation(
    state: dto.PatchEvaluationSchema, config: RunnableConfig
) -> dict[str, typing.Any]:
    """Get the evaluation of a patch."""
    registry = utils.get_registry_from_config(config)
    client = registry.get_service(clients.HBITClient)
    summary_service = registry.get_service(summaries.SummaryService)

    try:
        evaluation = client.get_patch_evaluation(patch_build=state["patch_build"])
        summary = summary_service.generate_summary(evaluation)
        message = AIMessage(
            f"Success: Action {enums.GraphAction.PATCH_EVALUATION} created evaluation:\n{summary}"
        )
        return {"messages": message}
    except Exception as error:
        message = AIMessage(f"Error occurred: {error}")
        return {"messages": message}


def get_device_identifier(
    state: dto.ExtractionSchema, config: RunnableConfig
) -> dict[str, typing.Any]:
    """Get device identifier from any text. Return None if no device was found."""
    registry = utils.get_registry_from_config(config)
    device_extractor = registry.get_service(extractors.DeviceExtractor)

    text = state["text"]
    device_identifier = device_extractor.extract_device_identifier(text=text)

    if device_identifier:
        message = AIMessage(
            f"Success: Action {enums.GraphAction.DEVICE_EXTRACTION} extracted device identifier: {device_identifier} from text '{text}'."
        )
    else:
        message = AIMessage(
            f"Error: No device identifier was found in text '{text}'. Ask user for more information about the device."
        )

    return {"messages": message}


def get_patch_build(
    state: dto.ExtractionSchema, config: RunnableConfig
) -> dict[str, typing.Any]:
    """Get patch build from any text. Return None if no patch was found."""
    registry = utils.get_registry_from_config(config)
    patch_extractor = registry.get_service(extractors.PatchExtractor)

    text = state["text"]
    patch_build = patch_extractor.extract_patch_build(text=text)

    if patch_build:
        message = AIMessage(
            f"Success: Action {enums.GraphAction.PATCH_EXTRACTION} extracted patch build: {patch_build} from text '{text}'."
        )
    else:
        message = AIMessage(
            f"Error: No patch build was found in text '{text}'. Ask user for more information about the patch."
        )

    return {"messages": message}
