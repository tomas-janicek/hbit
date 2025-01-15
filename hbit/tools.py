import typing

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool  # type: ignore
from langchain_core.tools.base import BaseTool, InjectedToolCallId
from langgraph.prebuilt import InjectedState  # type: ignore
from langgraph.types import Command

from common import requests
from hbit import clients, core, dto, evaluations, models, settings, summaries, utils
from hbit.extractors import device_extractors, patch_extractors


@tool(return_direct=True)
def generate_evaluation_summary(
    state: typing.Annotated[dto.AgentStateSchema, InjectedState],
) -> str:
    """Generate summary from evaluation."""
    summary_service = summaries.AiSummaryService(
        summary_model=models.smaller_model, analysis_model=models.default_model
    )
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
) -> Command:  # type: ignore
    """Input to this tool strings device identifier and patch build. Be sure that the
    device identifier and patch build have valid formats by calling get_device_identifier
    and get_patch_build! If device identifier or patch build is not correct, an error will
    be returned. If so, try using one of get_device_identifier or get_patch_build again.
    If you successfully retrieved evaluation, generate it's summary using
    generate_evaluation_summary tool.
    Example device identifier: 'iphone7,2', 'iphone9,4', 'iphone17,3'.
    Example patch build: '22b83', '21g93', '20h240', '19h370', '19b74'."""
    request = requests.HTTPXRequests(utils.create_hbit_api_client())
    hbit_client = clients.ApiHBITClient(
        request=request, hbit_api_url=settings.HBIT_API_URL
    )
    evaluation_service = evaluations.IterativeEvaluationService(hbit_client)
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
) -> str | None:
    """Get device identifier."""
    db = core.DatabaseService()
    device_extractor = device_extractors.StructureDeviceExtractor(
        model=models.code_model, db=db
    )
    question = str(state["messages"][0].content)
    device_identifier = device_extractor.extract_device_identifier(text=question)
    return device_identifier


@tool
def get_patch_build(
    state: typing.Annotated[dto.QuestionStateSchema, InjectedState],
) -> str | None:
    """Get patch build."""
    db = core.DatabaseService()
    patch_extractor = patch_extractors.StructurePatchExtractor(
        model=models.code_model, db=db
    )
    question = str(state["messages"][0].content)
    patch_build = patch_extractor.extract_patch_build(text=question)
    return patch_build


TOOLS: list[BaseTool] = [
    generate_evaluation_summary,
    get_device_evaluation,
    get_device_identifier,
    get_patch_build,
]
