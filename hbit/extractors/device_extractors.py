import logging
import typing

from langchain.prompts import (
    ChatPromptTemplate,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableSerializable
from sqlalchemy import text as _text

from hbit import core, dto, utils

from . import base

_log = logging.getLogger(__name__)


class StructureDeviceExtractor(base.DeviceExtractor):
    examples = (
        "Input Example: 'How secure is my iPhone 13 Pro device if I have patch 18.1.0 installed identified by build 22B83.'\n"
        f"Output Example: {{{dto.Device(identifier=None, name='iPhone 13 Pro', manufacturer=None, model=None).model_dump_json()}}}\n\n"
        "Input Example: 'How secure is my device with model Apple device with model A2483.'\n"
        f"Output Example: {{{dto.Device(identifier=None, name=None, manufacturer='Apple', model='a2483').model_dump_json()}}}\n\n"
        "Input Example: 'Should I buy new phone if I have iphone14,2.'\n"
        f"Output Example: {{{dto.Device(identifier='iphone14,2', name=None, manufacturer=None, model=None).model_dump_json()}}}\n\n"
        "Input Example: 'Is iPhone 6 and iphone7,2 the same device?'\n"
        f"Output Example: {{{dto.Device(identifier='iphone7,2', name='iPhone 6', manufacturer=None, model=None).model_dump_json()}}}\n\n"
        "Input Example: 'How secure is an iPhone XS running iOS 17.7.2? Are there any known vulnerabilities or security concerns with this version?'\n"
        f"Output Example: {{{dto.Device(identifier=None, name='iPhone XS', manufacturer=None, model=None).model_dump_json()}}}\n\n"
        "Input Example: 'Which version is my iPhone running if the patch is labeled with build 24D12?'\n"
        f"Output Example: {{{dto.Device(identifier=None, name=None, manufacturer=None, model=None).model_dump_json()}}}\n\n"
        "Input Example: 'Can you tell me the version number for the patch identified by build 23C45?'\n"
        f"Output Example: {{{dto.Device(identifier=None, name=None, manufacturer=None, model=None).model_dump_json()}}}\n\n"
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "Make sure you only extract the values of the attributes mentioned in the question. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.\n\n"
                "{examples}",
            ),
            ("human", "{input}"),
        ]
    )

    def __init__(self, model: BaseChatModel, db: core.DatabaseService) -> None:
        self.model = model
        self.db = db
        self.extractor_model: RunnableSerializable[
            dict[str, typing.Any], dto.Device
        ] = self.prompt_template | (
            self.model.with_structured_output(schema=dto.Device)
        )  # type: ignore

    def extract_device_identifier(self, text: str) -> str | None:
        device = self.extract_device_info(text)
        _log.debug(f"Extracted device: {device}")
        if utils.are_all_fields_none(device):
            return None

        with self.db.connect() as connection:
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

    def extract_device_info(self, text: str) -> dto.Device:
        device = self.extractor_model.invoke({"input": text, "examples": self.examples})
        return device


class SqlDeviceExtractor(base.DeviceExtractor):
    examples = (
        "Input Example: How secure is my iPhone 13 Pro device if I have patch 18.1.0 installed identified by build 22B83.\n"
        "Output Example: SELECT identifier FROM devices WHERE name LIKE '%iPhone 13 Pro%'\n\n"
        "Input Example: How secure is my device with model Apple device with model A2483.\n"
        "Output Example: SELECT identifier FROM devices WHERE models LIKE '%A2483%'\n\n"
        "Input Example: Should I buy new phone if I have iphone14,2.\n"
        "Output Example: SELECT identifier FROM devices WHERE identifier LIKE '%iphone14,2%'\n\n"
        "Input Example: Is iPhone 6 and iphone7,2 the same device?\n"
        "Output Example: SELECT identifier FROM devices WHERE identifier LIKE '%iphone7,2%' AND name LIKE '%iPhone 6%'\n\n"
        "Input Example: How secure is an iPhone XS running iOS 17.7.2? Are there any known vulnerabilities or security concerns with this version?\n"
        "Output Example: SELECT identifier FROM devices WHERE name LIKE '%iPhone XS%'\n\n"
        "Input Example: Which version is my iPhone running if the patch is labeled with build 24D12?\n"
        "Output Example: \n\n"
        "Input Example: Can you tell me the version number for the patch identified by build 23C45?\n"
        "Output Example: \n\n"
    )
    query_prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Your task is to generate a syntactically correct {dialect} query based on the given input question. "
                "The purpose of the query is to extract the `identifier` column from the `devices` table. "
                "If there is no mention of any device, return empty string instead of SQL query.\n"
                "Follow these guidelines:\n"
                "1. Only filter by values explicitly mentioned in the input question that are relevant to the device.\n"
                "2. Avoid querying columns that are not part of the schema or values do not resamble values in rows.\n"
                "3. Prioritize using unique columns that can independently identify a device by themselves.\n"
                "4. Use `LIKE` for string matching to ensure case-insensitive filtering.\n"
                "5. Completely ignore JSON fields.\n"
                "6. Make sure values you are filtering by resemble the values in the schema."
                "\n\n"
                "The schema of the `devices` table is as follows:\n"
                "{table_info}\n\n"
                "Examples:\n"
                "{examples}",
            ),
            ("user", "Question: {input}"),
        ]
    )

    def __init__(self, model: BaseChatModel, db: core.DatabaseService) -> None:
        self.model = model
        self.db = db

        self.structured_llm: RunnableSerializable[
            dict[str, typing.Any], dto.QueryOutput
        ] = self.query_prompt_template | self.model.with_structured_output(
            dto.QueryOutput
        )  # type: ignore

    def extract_device_identifier(self, text: str) -> str | None:
        query_output = self.create_extraction_query(text)
        _log.debug(f"Query: {query_output.query}")
        if not query_output.query:
            return None

        response = self.execute_query(query_output.query)
        return response

    def create_extraction_query(self, question: str) -> dto.QueryOutput:
        devices_table_info = self.db.get_table_info(["devices"])

        result: dto.QueryOutput = self.structured_llm.invoke(
            {
                "dialect": self.db.dialect,
                "table_info": devices_table_info,
                "input": question,
                "examples": self.examples,
            }
        )
        return result

    def execute_query(self, query: str) -> str:
        with self.db.connect() as connection:
            result = connection.scalar(_text(query))
        return result
