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


class Patch(BaseModel):
    build: str | None = Field(
        description="Unique build of the patch in format similar to '22B83'"
    )
    version: str | None = Field(
        description="Version of the patch in format similar to '18.1.0'"
    )


class StructurePatchExtractor(base.PatchExtractor):
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    patch_examples: typing.ClassVar[list[dict[str, str | Patch]]] = [
        {
            "input": "How secure is my iPhone 13 Pro patch if I have patch 18.1.0 installed identified by build 22B83.",
            "output": Patch(build="22B83", version="18.1.0"),
        },
    ]
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=patch_examples,
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
        self.extractor_model: Runnable[PromptValue, Patch] = (
            self.model.with_structured_output(schema=Patch)
        )  # type: ignore

    def extract_patch_info(self, text: str) -> Patch:
        prompt = self.prompt_template.invoke({"input": text})
        patch = self.extractor_model.invoke(prompt)
        return patch

    def extract_patch_build(self, text: str) -> str | None:
        patch = self.extract_patch_info(text)
        _log.debug(f"Extracted patch: {patch}")
        with engine.connect() as connection:
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
                    "version": patch.version,
                },
            )
        return result


class SqlPatchExtractor(base.PatchExtractor):
    query_prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Your task is to generate a syntactically correct {dialect} query based on the given input question. "
                "The purpose of the query is to extract the `build` column from the `patches` table. "
                "Follow these guidelines:\n"
                "1. Only filter by values explicitly mentioned in the input question that are relevant to the patch.\n"
                "2. Avoid querying columns that are not part of the schema or using incorrect example values.\n"
                "3. Prioritize using unique columns that can independently identify a patch.\n"
                "4. Use `LIKE` for string matching to ensure case-insensitive filtering.\n"
                "5. Do not apply any filtering on fields containing JSON data.\n\n"
                "The schema of the `patches` table is as follows:\n"
                "{table_info}\n",
            ),
            ("user", "Question: {input}"),
        ]
    )

    def __init__(self, model: BaseChatModel) -> None:
        self.model = model

    def extract_patch_build(self, text: str) -> str:
        query_output = self.create_extraction_query(text)
        _log.debug(f"Query: {query_output.query}")

        response = self.execute_query(query_output.query)
        return response

    def create_extraction_query(self, question: str) -> dto.QueryOutput:
        patches_table_info = db.get_table_info(["patches"])

        prompt = self.query_prompt_template.invoke(
            {
                "dialect": db.dialect,
                "table_info": patches_table_info,
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
