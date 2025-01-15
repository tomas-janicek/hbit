import typing

import pydantic
from langchain.schema import BaseMessage
from langgraph.graph import add_messages  # type: ignore
from langgraph.managed import IsLastStep, RemainingSteps  # type: ignore

from common import dto as common_dto


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


class AgentStateSchema(typing.TypedDict):
    messages: typing.Annotated[list[BaseMessage], add_messages]
    device_evaluation: common_dto.EvaluationDto

    is_last_step: IsLastStep
    remaining_steps: RemainingSteps


class QuestionStateSchema(typing.TypedDict):
    messages: typing.Annotated[list[BaseMessage], add_messages]


class ChainStateSchema(typing.TypedDict):
    messages: typing.Annotated[typing.Sequence[BaseMessage], add_messages]

    question: str
    device_identifier: str
    patch_build: str
    device_evaluation: common_dto.EvaluationDto
    device_summary: str
