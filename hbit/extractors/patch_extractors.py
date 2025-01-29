import logging
import typing

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableSerializable
from sqlalchemy import text as _text

from hbit import core, dto, prompting, utils

from . import base

_log = logging.getLogger(__name__)


class JsonPatchExtractor(base.PatchExtractor):
    def __init__(
        self,
        model: BaseChatModel,
        db: core.DatabaseService,
        prompt_store: prompting.PromptStore,
    ) -> None:
        self.model = model
        self.db = db
        self.prompt_store = prompt_store

        self.extractor_model: RunnableSerializable[dict[str, typing.Any], dto.Patch] = (
            self.prompt_store.patch_json_extraction
            | self.model.with_structured_output(schema=dto.Patch)
        )  # type: ignore

    def extract_patch_build(self, text: str) -> str | None:
        patch = self.extract_patch_info(text)
        _log.debug(f"Extracted patch: {patch}")
        if utils.are_all_fields_none(patch):
            return None

        with self.db.connect() as connection:
            raw_sql = (
                "SELECT patches.build "
                "FROM patches as patches "
                "WHERE (:build is null OR patches.build like :build) "
                "AND (:version is null OR patches.version like :version);"
            )
            result = connection.scalar(
                _text(raw_sql),
                parameters={
                    "build": patch.build,
                    "version": f"%{patch.version}%" if patch.version else None,
                },
            )
        return result

    def extract_patch_info(self, text: str) -> dto.Patch:
        patch = self.extractor_model.invoke({"input": text})
        return patch


class SqlPatchExtractor(base.PatchExtractor):
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
        ] = self.prompt_store.patch_sql_extraction | self.model.with_structured_output(
            dto.QueryOutput
        )  # type: ignore

    def extract_patch_build(self, text: str) -> str | None:
        query_output = self.create_extraction_query(text)
        if not query_output.query:
            return None

        _log.debug(f"Query: {query_output.query}")
        response = self.execute_query(query_output.query)
        return response

    def create_extraction_query(self, question: str) -> dto.QueryOutput:
        patches_table_info = self.db.get_table_info(["patches"])

        result: dto.QueryOutput = self.structured_llm.invoke(
            {
                "dialect": self.db.dialect,
                "table_info": patches_table_info,
                "input": question,
            }
        )
        return result

    def execute_query(self, query: str) -> str:
        with self.db.connect() as connection:
            result = connection.scalar(_text(query))
        return result
