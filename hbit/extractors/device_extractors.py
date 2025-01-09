import logging
import typing

from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseChatModel
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import Runnable
from pydantic import BaseModel, Field
from sqlalchemy import text as _text

from hbit import dto, settings
from hbit.core import engine

from . import base

_log = logging.getLogger(__name__)

# TODO: Extract to core module (or not use at all)
db = SQLDatabase.from_uri(
    settings.READ_SQLALCHEMY_DATABASE_URI, sample_rows_in_table_info=10
)


class Device(BaseModel):
    identifier: str | None = Field(
        description="Unique identifier of the device in format similar to 'iphone14,2'"
    )
    name: str | None = Field(
        description="Human readable device name in format similar to 'iPhone 13 Pro'"
    )
    manufacturer: str | None = Field(description="Manufacturer of the device")
    model: str | None = Field(
        description="Model of the device in format usually starting with 'A' or 'a' followed by numbers"
    )


class StructureDeviceExtractor(base.DeviceExtractor):
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    device_examples: typing.ClassVar[list[dict[str, str | Device]]] = [
        {
            "input": "How secure is my iPhone 13 Pro device if I have patch 18.1.0 installed identified by build 22B83.",
            "output": Device(
                identifier=None, name="iPhone 13 Pro", manufacturer=None, model=None
            ),
        },
        {
            "input": "How secure is my device with model Apple device with model A2483.",
            "output": Device(
                identifier=None, name=None, manufacturer="Apple", model="a2483"
            ),
        },
        {
            "input": "Should I buy new phone if I have iphone14,2.",
            "output": Device(
                identifier="iphone14,2", name=None, manufacturer=None, model=None
            ),
        },
        {
            "input": "Is iPhone 6 and iphone7,2 the same device?",
            "output": Device(
                identifier="iphone7,2", name="iPhone 6", manufacturer=None, model=None
            ),
        },
    ]
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=device_examples,
    )
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "Make sure you only extract the values of the attributes mentioned in the question. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.",
            ),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )

    def __init__(self, model: BaseChatModel) -> None:
        self.model = model
        self.extractor_model: Runnable[PromptValue, Device] = (
            self.model.with_structured_output(schema=Device)
        )  # type: ignore

    def extract_device_info(self, text: str) -> Device:
        prompt = self.prompt_template.invoke({"input": text})
        device = self.extractor_model.invoke(prompt)
        return device

    def extract_device_identifier(self, text: str) -> str | None:
        device = self.extract_device_info(text)
        _log.debug(f"Extracted device: {device}")
        with engine.connect() as connection:
            raw_sql = (
                "SELECT devices.identifier "
                "FROM devices as devices "
                "JOIN manufacturers as manufacturers "
                "ON (devices.manufacturer_id = manufacturers.id) "
                "WHERE (:identifier is null OR devices.identifier like :identifier) "
                "AND (:name is null OR devices.name like :name) "
                "AND (:manufacturer is null OR manufacturers.name like :manufacturer) "
                "AND (:model is null OR devices.models like :model);"
            )
            result = connection.scalar(
                _text(raw_sql),
                parameters={
                    "identifier": device.identifier,
                    "name": device.name,
                    "manufacturer": device.manufacturer,
                    "model": f"%{device.model}%" if device.model else None,
                },
            )
        return result


class SqlDeviceExtractor(base.DeviceExtractor):
    query_prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are tasked with generating a syntactically correct {dialect} query based on an input question. "
                "The goal is to extract the `identifier` column from the `devices` table. Ensure the query only filters "
                "by values explicitly mentioned in the input question that are relevant to the device. "
                "Avoid querying columns that do not exist in the schema or using incorrect values as examples. "
                "Focus solely on the `identifier` column in your output. "
                "Do not apply any filtering in fields that contain JSON data.\n\n"
                "The schema of the `devices` table is as follows:\n"
                "{table_info}\n",
            ),
            ("user", "Question: {input}"),
        ]
    )
    query_prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Your task is to generate a syntactically correct {dialect} query based on the given input question. "
                "The purpose of the query is to extract the `identifier` column from the `devices` table. "
                "Follow these guidelines:\n"
                "1. Only filter by values explicitly mentioned in the input question that are relevant to the device.\n"
                "2. Avoid querying columns that are not part of the schema or using incorrect example values.\n"
                "3. Prioritize using unique columns that can independently identify a device.\n"
                "4. Use `LIKE` for string matching to ensure case-insensitive filtering.\n"
                "5. Do not apply any filtering on fields containing JSON data.\n"
                "6. Make sure values you are filtering by resemble the values in the schema."
                "\n\n"
                "The schema of the `devices` table is as follows:\n"
                "{table_info}\n",
            ),
            ("user", "Question: {input}"),
        ]
    )

    def __init__(self, model: BaseChatModel) -> None:
        self.model = model

    def extract_device_identifier(self, text: str) -> str:
        query_output = self.create_extraction_query(text)
        _log.debug(f"Query: {query_output.query}")

        response = self.execute_query(query_output.query)
        return response

    def create_extraction_query(self, question: str) -> dto.QueryOutput:
        devices_table_info = db.get_table_info(["devices"])

        prompt = self.query_prompt_template.invoke(
            {
                "dialect": db.dialect,
                "table_info": devices_table_info,
                "input": question,
            }
        )

        structured_llm = self.model.with_structured_output(dto.QueryOutput)  # type: ignore
        result: dto.QueryOutput = structured_llm.invoke(prompt)  # type: ignore
        return result

    def execute_query(self, query: str) -> str:
        with engine.connect() as connection:
            result = connection.scalar(_text(query))
        return result
