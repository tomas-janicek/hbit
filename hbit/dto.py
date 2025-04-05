import typing

import pydantic
from langchain.schema import BaseMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep, RemainingSteps

from common import dto as common_dto
from hbit import enums

######################
# Structured Outputs #
######################


class QueryOutput(pydantic.BaseModel):
    """Generated SQL query."""

    query: typing.Annotated[str, ..., "Syntactically valid SQL query."]


class Device(pydantic.BaseModel):
    identifier: str | None = pydantic.Field(
        description="Unique identifier of the device in format similar to 'iphone14,2'"
    )
    name: str | None = pydantic.Field(
        description="Human readable device name in format similar to 'iPhone 13 Pro'"
    )
    manufacturer: str | None = pydantic.Field(description="Manufacturer of the device")
    model: str | None = pydantic.Field(
        description="Model of the device in format usually starting with 'A' or 'a' followed by numbers"
    )


class Patch(pydantic.BaseModel):
    build: str | None = pydantic.Field(
        None, description="Unique build of the patch in format similar to '22B83'"
    )
    version: str | None = pydantic.Field(
        None, description="Version of the patch in format similar to '18.1.0'"
    )


class ExtractionText(pydantic.BaseModel):
    text: str = pydantic.Field(
        description="Text required for extraction of device or patch information. Must be string provided by user."
    )


class DeviceEvaluationParameters(pydantic.BaseModel):
    device_identifier: str = pydantic.Field(
        description="Unique identifier of the device in format similar to 'iphone14,2'"
    )
    patch_build: str = pydantic.Field(
        description="Unique build of the patch in format similar to '22B83'"
    )


class PatchEvaluationParameters(pydantic.BaseModel):
    patch_build: str = pydantic.Field(
        description="Unique build of the patch in format similar to '22B83'"
    )


class GraphRouterResponse(pydantic.BaseModel):
    action: enums.GraphAction
    data: ExtractionText | DeviceEvaluationParameters | PatchEvaluationParameters | None


class SecurityPaper(pydantic.BaseModel):
    text: str
    category: enums.SecurityPaperCategory

    def __str__(self) -> str:
        return f"Category: {self.category.value}\nText: {self.text}\n"


class SecurityPaperQuery(pydantic.BaseModel):
    category: enums.SecurityPaperCategory | None = None


class SecurityPaperResponse(pydantic.BaseModel):
    security_paper: SecurityPaper
    distance: float


#################
# State Schemas #
#################


class AgentStateSchema(typing.TypedDict):
    messages: typing.Annotated[typing.Sequence[BaseMessage], add_messages]

    evaluation: common_dto.EvaluationDto | None

    is_last_step: IsLastStep
    remaining_steps: RemainingSteps


class GraphStateSchema(typing.TypedDict):
    messages: typing.Annotated[list[BaseMessage], add_messages]
    max_steps: int
    current_step: int


class ExtractionType(typing.TypedDict):
    messages: list[BaseMessage]
    extraction_type: typing.Literal["device", "patch"]


class ExtractionSchema(typing.TypedDict):
    text: str


class DeviceExtractionSchema(ExtractionSchema):
    pass


class PatchExtractionSchema(ExtractionSchema):
    pass


class PatchEvaluationSchema(typing.TypedDict):
    patch_build: str


class DeviceEvaluationSchema(typing.TypedDict):
    device_identifier: str
    patch_build: str
