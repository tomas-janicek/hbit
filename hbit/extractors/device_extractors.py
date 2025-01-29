import logging
import typing

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableSerializable
from sqlalchemy import text as _text

from hbit import core, dto, prompting, utils

from . import base

_log = logging.getLogger(__name__)


class JsonDeviceExtractor(base.DeviceExtractor):
    def __init__(
        self,
        model: BaseChatModel,
        db: core.DatabaseService,
        prompt_store: prompting.PromptStore,
    ) -> None:
        self.model = model
        self.db = db
        self.prompt_store = prompt_store

        self.extractor_model: RunnableSerializable[
            dict[str, typing.Any], dto.Device
        ] = self.prompt_store.device_json_extraction | (
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
        device = self.extractor_model.invoke({"input": text})
        return device


class SqlDeviceExtractor(base.DeviceExtractor):
    def __init__(
        self,
        model: BaseChatModel,
        db: core.DatabaseService,
        prompt_store: prompting.PromptStore,
    ) -> None:
        self.model = model
        self.db = db
        self.prompt_store = prompt_store

        self.structured_llm: RunnableSerializable[
            dict[str, typing.Any], dto.QueryOutput
        ] = self.prompt_store.device_sql_extraction | self.model.with_structured_output(
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
            }
        )
        return result

    def execute_query(self, query: str) -> str:
        with self.db.connect() as connection:
            result = connection.scalar(_text(query))
        return result
