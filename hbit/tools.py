import typing

from langchain_core.tools import tool  # type: ignore
from langchain_core.tools.base import BaseTool

from common import dto as common_dto
from common import requests
from hbit import clients, core, evaluations, models, settings, summaries, utils
from hbit.extractors import device_extractors, patch_extractors


@tool
def generate_evaluation_summary(
    question: typing.Annotated[str, "User's question."],
    evaluation: common_dto.EvaluationDto,
) -> str:
    """Generate summary from users question and evaluation."""
    summary_service = summaries.AiSummaryService(model=models.smaller_model)
    summary = summary_service.generate_summary(question=question, evaluation=evaluation)
    return summary


@tool
def get_device_evaluation(
    device_identifier: typing.Annotated[
        str, "Unique identifier of the device in format similar to 'iphone14,2'"
    ],
    patch_build: typing.Annotated[
        str, "Unique build of the patch in format similar to '22B83'"
    ],
) -> common_dto.EvaluationDto | None:
    """Get the evaluation of a device."""
    request = requests.HTTPXRequests(utils.create_hbit_api_client())
    hbit_client = clients.ApiHBITClient(
        request=request, hbit_api_url=settings.HBIT_API_URL
    )
    evaluation_service = evaluations.IterativeEvaluationService(hbit_client)
    evaluation = evaluation_service.get_trimmed_evaluation(
        device_identifier, patch_build
    )
    return evaluation


@tool
def get_device_identifier(
    question: typing.Annotated[str, "User's question."],
) -> str | None:
    """Get device identifier from any text. Return None if no device was found."""
    db = core.DatabaseService()
    device_extractor = device_extractors.StructureDeviceExtractor(
        model=models.code_model, db=db
    )
    device_identifier = device_extractor.extract_device_identifier(text=question)
    return device_identifier


@tool
def get_patch_build(
    question: typing.Annotated[str, "User's question."],
) -> str | None:
    """Get patch build from any text. Return None if no patch was found."""
    db = core.DatabaseService()
    patch_extractor = patch_extractors.StructurePatchExtractor(
        model=models.code_model, db=db
    )
    patch_build = patch_extractor.extract_patch_build(text=question)
    return patch_build


TOOLS: list[BaseTool] = [
    generate_evaluation_summary,
    get_device_evaluation,
    get_device_identifier,
    get_patch_build,
]
